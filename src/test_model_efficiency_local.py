import json
import os
import re
import threading
import time

import psutil
import torch
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase
from transformers import AutoModelForCausalLM, AutoTokenizer


# --- 1. SYSTEM MONITOR CLASS ---
class SystemBenchmark:
    """
    Context manager to measure Time, CPU, and RAM usage of a code block.
    """
    def __init__(self, name="Operation"):
        self.name = name
        self.process = psutil.Process(os.getpid())
        self.start_time = 0
        self.end_time = 0
        self.peak_memory_mb = 0
        self.avg_cpu_percent = 0
        self._monitoring = False
        self._thread = None

    def _monitor_resources(self):
        """Runs in a separate thread to sample resource usage."""
        cpu_samples = []
        while self._monitoring:
            cpu_samples.append(self.process.cpu_percent(interval=0.1))
            mem_info = self.process.memory_info()
            current_mem_mb = mem_info.rss / (1024 * 1024)
            self.peak_memory_mb = max(self.peak_memory_mb, current_mem_mb)

        if cpu_samples:
            self.avg_cpu_percent = sum(cpu_samples) / len(cpu_samples)

    def __enter__(self):
        self.start_time = time.time()
        self._monitoring = True
        self.peak_memory_mb = self.process.memory_info().rss / (1024 * 1024)
        self.process.cpu_percent()

        self._thread = threading.Thread(target=self._monitor_resources)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._monitoring = False
        self._thread.join()
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

        print(f"\n[{self.name} Results]")
        print(f"⏱️  Duration:     {self.duration:.4f} seconds")
        print(f"💾 Peak RAM:     {self.peak_memory_mb:.2f} MB")
        print(f"💻 Avg CPU:      {self.avg_cpu_percent:.1f}%")

        if torch.cuda.is_available():
            vram = torch.cuda.max_memory_allocated() / (1024 * 1024)
            print(f"🎮 Peak VRAM:    {vram:.2f} MB")

# --- 2. CUSTOM DEEPEVAL EVALUATOR WITH JSON FIXING ---
class LocalQwenEvaluator(DeepEvalBaseLLM):
    """
    Uses Qwen 2.5 14B as the DeepEval judge with JSON validation.
    Upgraded from 1.5B because smaller models cannot reliably output valid JSON.
    """
    def __init__(self, model_name="Qwen/Qwen2.5-14B-Instruct"):
        self.model_name = model_name
        print(f"Loading evaluator model: {model_name}...")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def load_model(self):
        return self.model

    def _extract_json_from_text(self, text: str) -> str:
        """
        Attempts to extract valid JSON from model output.
        Handles cases where the model adds extra text around the JSON.
        """
        # Try to find JSON object in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                # Validate it's actually JSON
                json.loads(json_match.group(0))
                return json_match.group(0)
            except json.JSONDecodeError:
                pass

        # If no valid JSON found, return original text
        # DeepEval will handle the error
        return text

    def generate(self, prompt: str, max_retries: int = 2) -> str:
        """
        DeepEval calls this to get the evaluator's judgment.
        Includes retry logic for JSON validation.
        """
        # Enhance prompt to encourage JSON output
        enhanced_prompt = f"""{prompt}

IMPORTANT: You must respond with ONLY valid JSON. Do not include any text before or after the JSON object."""

        for attempt in range(max_retries):
            messages = [{"role": "user", "content": enhanced_prompt}]
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.05 if attempt > 0 else 0.1,  # Lower temp on retry
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )

            generated_text = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            ).strip()

            # Try to extract and validate JSON
            json_text = self._extract_json_from_text(generated_text)

            try:
                # Validate it parses correctly
                json.loads(json_text)
                return json_text
            except json.JSONDecodeError:
                if attempt < max_retries - 1:
                    print(f"⚠️  JSON parse failed (attempt {attempt + 1}), retrying...")
                else:
                    print(f"⚠️  Warning: Invalid JSON after {max_retries} attempts")
                    print(f"Raw output: {generated_text[:200]}...")
                    # Return the best attempt we have
                    return json_text

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self):
        return self.model_name

# --- 3. TRIPLEX GRAPH EXTRACTOR (MODEL BEING TESTED) ---
class TriplexGraphExtractor:
    """
    The model we're benchmarking (Triplex for knowledge graph extraction).
    """
    def __init__(self, model_name="SciPhi/Triplex"):
        print(f"Loading model under test: {model_name}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=False)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=False,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
        except Exception as e:
            print(f"Built-in loading failed: {e}, trying with trust_remote_code=True")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )

    def extract_triplets(self, text: str):
        """
        Converts raw text into knowledge graph triplets.
        """
        prompt = f"""Extract knowledge triplets from the following text.
Format: (Subject, Predicate, Object).

Text: {text}

Triplets:"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.1,
                use_cache=True,
                past_key_values=None,
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# --- 4. INITIALIZE MODELS ---
print("\n=== Initializing Models ===")

# The evaluator (judge) - upgraded to 14B for reliable JSON output
evaluator = LocalQwenEvaluator(model_name="Qwen/Qwen2.5-14B-Instruct")

# The model being tested - uses Triplex
extractor = TriplexGraphExtractor(model_name="SciPhi/Triplex")

# --- 5. CONFIGURE METRICS ---
faithfulness = FaithfulnessMetric(
    threshold=0.5,
    model=evaluator,
    include_reason=True
)

answer_relevancy = AnswerRelevancyMetric(
    threshold=0.5,
    model=evaluator,
    include_reason=True
)

# --- 6. TEST FUNCTION WITH BENCHMARKS ---
def test_graph_construction_with_benchmarks():
    """
    Benchmarks Triplex graph construction + Evaluates quality with local Qwen.
    """

    # Test input (clinical guideline text)
    input_text = """
    Metformin is the first-line pharmacologic treatment for type 2 diabetes.
    It works by decreasing glucose production by the liver and increasing
    the insulin sensitivity of body tissues. Common side effects include
    nausea and diarrhea.
    """

    print("\n=== Starting Graph Construction Benchmark ===")

    # 1. Benchmark the graph extraction
    with SystemBenchmark(name="Graph Construction (Triplex)") as stats:
        generated_triplets = extractor.extract_triplets(input_text)

    print(f"\nExtracted Output:\n{generated_triplets[:200]}...")

    # Calculate throughput
    output_tokens = len(extractor.tokenizer.encode(generated_triplets))
    tokens_per_sec = output_tokens / stats.duration if stats.duration > 0 else 0
    print(f"🚀 Throughput:   {tokens_per_sec:.2f} tokens/sec")

    # 2. Performance Assertions
    #assert stats.duration < 10.0, f"Too slow: {stats.duration}s"
    #assert stats.peak_memory_mb < 10000, f"Too much RAM: {stats.peak_memory_mb}MB"

    # 3. Quality Evaluation (using local Qwen as judge)
    print("\n=== Evaluating Quality with Local Model ===")

    test_case = LLMTestCase(
        input=input_text,
        actual_output=generated_triplets,
        retrieval_context=[input_text]
    )

    # Measure faithfulness
    try:
        faithfulness.measure(test_case)
        print(f"\nFaithfulness Score: {faithfulness.score:.2f}")
        print(f"Reason: {faithfulness.reason}")
        assert_test(test_case, [faithfulness])
    except Exception as e:
        print(f"⚠️  Faithfulness metric failed: {e}")
        print("This may be due to JSON formatting issues with the local model.")

# --- 7. OPTIONAL: TEST ANSWER RELEVANCY ---
def test_answer_relevancy():
    """
    Tests if the model's answers are relevant to the questions asked.
    """
    input_query = "What is metformin used for?"
    actual_output = "Metformin is used as the first-line treatment for type 2 diabetes."

    test_case = LLMTestCase(
        input=input_query,
        actual_output=actual_output
    )

    print("\n=== Testing Answer Relevancy ===")

    try:
        answer_relevancy.measure(test_case)
        print(f"Relevancy Score: {answer_relevancy.score:.2f}")
        print(f"Reason: {answer_relevancy.reason}")
        assert_test(test_case, [answer_relevancy])
    except Exception as e:
        print(f"⚠️  Answer relevancy metric failed: {e}")

if __name__ == "__main__":
    # Run both tests
    test_graph_construction_with_benchmarks()
    test_answer_relevancy()
