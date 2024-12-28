---
layout: default
title: "Async"
parent: "Core Abstraction"
nav_order: 5
---

# Async

**Async** pattern allows the `post()` step to be asynchronous (`post_async()`). This is especially helpful if you need to **await** something in `post_async()`—for example, user feedback or external async requests.

**Warning**: Only `post()` is async. `prep()` and `exec()` must be sync (often used for LLM calls).

---

## 1. AsyncNode

Below is a minimal **AsyncNode** that calls an LLM in `exec()` (sync) and then awaits user feedback in `post_async()`:

```python
class SummarizeThenVerify(AsyncNode):
    def exec(self, shared, prep_res):
        doc = shared.get("doc", "")
        return call_llm(f"Summarize: {doc}")

    async def post_async(self, shared, prep_res, exec_res):
        user_decision = await gather_user_feedback(exec_res)
        if user_decision == "approve":
            shared["summary"] = exec_res
            return "approve"
        else:
            return "deny"
```

---

## 2. AsyncFlow

We can build an **AsyncFlow** around this node. If the user denies, we loop back for another attempt; if approved, we pass to a final node:

```python
summarize_node = SummarizeThenVerify()
final_node = Finalize()

# Chain conditions
summarize_node - "approve" >> final_node
summarize_node - "deny" >> summarize_node  # retry loop

flow = AsyncFlow(start=summarize_node)

async def main():
    shared = {"doc": "Mini LLM Flow is a lightweight LLM framework."}
    await flow.run_async(shared)
    print("Final stored summary:", shared.get("final_summary"))

asyncio.run(main())
```

- **SummarizeThenVerify**: 
  - `exec()`: Summarizes text (sync LLM call).
  - `post_async()`: Waits for user approval.
- **Finalize**: Makes a final LLM call and prints the summary.
- If user denies, the flow loops back to **SummarizeThenVerify**.

