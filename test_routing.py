# test_routing.py
from expert_registry import ExpertiseRegistry

reg = ExpertiseRegistry()

print("\n--- TESTING HDFC ---")
hdfc_context = reg.get_skill_context("HDFCBANK.NS")
print(f"RESULT: {hdfc_context[:200]}...") # Should show NIM/CASA

print("\n--- TESTING TCS ---")
tcs_context = reg.get_skill_context("TCS.NS")
print(f"RESULT: {tcs_context[:200]}...") # Should show Attrition/Order Book