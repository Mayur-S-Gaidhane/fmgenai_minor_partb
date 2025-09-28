# LLM_Usage.md

List any places you used an LLM - GPT-5 during this Part B Q1 and Q2 .

- ** Create 20 semantically equivalent prompts across the English, Marathi, Hinglish languages (e.g., concise fact Q&A,
short reasoning, or brief instructions). Provide an answer key in any one language.
Add one code‑switch variant per prompt (e.g., sentence‑level alternation, or “question in
L2, answer requested in L1”)and geneate CSV file .**
== > Output response saved in data/q1_prompts.csv

- **One doubt Here i am using openai and ollama . Can we get their API key ? Are their key has any charges . I am a student . can not paid a charges .** 
== > That’s an excellent and very important question 🙌

Let me clarify the OpenAI vs Ollama situation for you:

🔹 1. OpenAI API

To use OpenAI models (like GPT-4, GPT-4o, GPT-3.5), you need an API key from platform.openai.com
.

Charges: Yes, usage is billed per token (input + output).

Example: GPT-4o mini is very cheap (fractions of a cent per request), but still not free.

Student discounts: OpenAI sometimes gives free credits (e.g., $5–$18) when you first sign up, but after that, you need to add billing.

👉 If you don’t want to spend money, this option is not ideal.

🔹 2. Ollama (Local, Free)

Ollama lets you run open-source models (LLaMA-3, Mistral, etc.) locally on your computer.

No API key needed.

No cost (other than disk space + RAM usage).

You just run ollama run llama3 (or whichever model you pull).

Works offline.

Downside: Models may be slower and less accurate compared to GPT-4.

👉 As a student who cannot pay, Ollama is the best option for you.

🔹 3. Recommendation for You

Since you said you can’t pay:
✅ Use Ollama for all your assignment runs.
Download & install from 👉 https://ollama.com/download

Then pull a model:

ollama pull llama3.1:8b-instruct


- **Is llama3.1:8b suitable for local system ? is there any ligher verion avaliable:** 
== >  llama3.1:8b will download the model (~4–5 GB). It may take some time.
If that feels too heavy for your laptop, you can instead pull a smaller one, e.g. ollama pull mistral:7b-instruct which is ~2–3 GB.
Can you tell me your laptop’s RAM size (e.g., 8 GB, 16 GB)? That will help me see if mistral:7b-instruct is a good fit or if we should pick an even lighter model.


NOTE : I am aware that my evaluate_q1.py foes not generate fluecy score .it kept on user to decide how much it is related . post eveluation of results/q1_results.csv on VS code . user have to give that score .

- **Uploaded my fluency_avg.py and its output (fmgenai) PS C:\Users\MayurGaidhane\Downloads\FM and GenAI\Minor\Part_B> python fluency_avg.py
Average Fluency Scores (1–5):
Empty DataFrame
Columns: [condition, avg_fluency, n_rated]
Index: []
and random output lines from result/q1_result.csv to get fluency score:**.
== > it gave me a one code name as "test.py" it shows output fluency score = NuN
I have share the output of it got below response 

Pandas is seeing the fluency column but it’s empty (NaN) in your file. That usually means the numbers you typed landed in another column (e.g., because of trailing commas or multiline fields).

and provided me updated code save as "fluency_probe_and_avg.py"


