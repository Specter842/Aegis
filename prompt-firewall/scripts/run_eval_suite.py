import asyncio
import json
import httpx
import os

API_URL = "http://localhost:8000/v1/proxy/chat"

async def evaluate_dataset(file_path: str, is_malicious_expected: bool):
    results = []
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return results

    async with httpx.AsyncClient() as client:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                prompt = data.get("prompt")
                
                payload = {
                    "request_id": f"eval_req",
                    "tenant_id": "eval",
                    "app_id": "demo",
                    "prompt": prompt,
                    "target": {"provider": "openai", "model": "gpt-4"}
                }
                
                try:
                    res = await client.post(API_URL, json=payload, timeout=30.0)
                    response_data = res.json()
                    
                    # Determine actual decision
                    decision = response_data.get('decision')
                    output_scan = response_data.get('output_scan', {})
                    if output_scan.get('blocked'):
                        decision = "block"
                        
                    is_blocked = decision == "block"
                    
                    # True Positive: Expected Malicious, and was Blocked
                    # False Negative: Expected Malicious, but was Allowed
                    # True Negative: Expected Benign, and was Allowed
                    # False Positive: Expected Benign, but was Blocked
                    
                    if is_malicious_expected:
                        outcome = "TP" if is_blocked else "FN"
                    else:
                        outcome = "TN" if not is_blocked else "FP"
                        
                    results.append(outcome)
                except Exception as e:
                    print(f"Error evaluating prompt: {prompt[:30]}... - {e}")
                    
    return results

async def main():
    print("Running AEGIS Evaluation Suite...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    attacks_file = os.path.join(base_dir, "evals", "datasets", "attacks.jsonl")
    benign_file = os.path.join(base_dir, "evals", "datasets", "benign.jsonl")
    leaks_file = os.path.join(base_dir, "evals", "datasets", "output_leaks.jsonl")
    
    print("\n1. Evaluating attacks.jsonl (Expected Malicious)")
    attack_results = await evaluate_dataset(attacks_file, is_malicious_expected=True)
    
    print("2. Evaluating output_leaks.jsonl (Expected Malicious)")
    leak_results = await evaluate_dataset(leaks_file, is_malicious_expected=True)
    
    print("3. Evaluating benign.jsonl (Expected Benign)")
    benign_results = await evaluate_dataset(benign_file, is_malicious_expected=False)
    
    all_results = attack_results + leak_results + benign_results
    
    tp = all_results.count("TP")
    fn = all_results.count("FN")
    tn = all_results.count("TN")
    fp = all_results.count("FP")
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
    
    print("\n==================================")
    print("        EVALUATION METRICS        ")
    print("==================================")
    print(f"Total Samples: {len(all_results)}")
    print(f"True Positives (TP) : {tp}")
    print(f"False Positives (FP): {fp}")
    print(f"True Negatives (TN) : {tn}")
    print(f"False Negatives (FN): {fn}")
    print("----------------------------------")
    print(f"Precision : {precision:.2f}")
    print(f"Recall    : {recall:.2f}")
    print(f"F1 Score  : {f1:.2f}")
    print(f"FPR       : {fpr:.2f} (False Positive Rate)")
    print(f"FNR       : {fnr:.2f} (False Negative Rate)")
    print("==================================")

if __name__ == "__main__":
    asyncio.run(main())
