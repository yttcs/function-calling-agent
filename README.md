## Barebones function calling agent using the following technology: 

1. Backend: FastAPI, MariaDB, SQL Model, OpenAI completions API, Tavily Search API
2. Frontend: Jinja2, JS, HTMX, Bootstrap
3. Security: Oauth2 password grant (ROPC)
4. Infrastructure: AWS ECS/Fargate and DigitalOcean

This is a work in progress and it's planned to have multiple updates on a weekly basis.

### Update for week of Jun. 30, 2025:

1. Added multiuser capability
2. Added Tavily Extract API
3. Switched from gpt-3.5-turbo to gpt-4o

### Update for week of Jul. 21, 2025:

1. Added text to speech using gpt-4o-mini-tts for completion.choices[0].message.content (that means the agent now has a voice)

### Note: Update for week of Aug. 11, 2025:
1. Addied speech to text and text to speech using and Whisper and gpt-4o-mini-transcribe 
2. Added UTX date tool and time tools so the model can be time aware

### Note: Update for week of Oct. 20, 2025:

1. Added database persistence, for conversation history, in combination with in-memory python dict
2. Employed a hybrid HTMX/JS solution to play TTS in browser from text and voice requests
3. Added some error handling
4. Added HTMX to avoid full page refreshes
5. Cleaned up UI
6. Switched to gpt-4o-mini
7. Containerized with Podman
8. Deployed to AWS ECS/Fargate:  SENTyENT.com

Will work on issues here and there, but, for the most part, this web PoC is finished. Focusing on local and offgrid now.
One issue to be solved is that, in chromium based browsers, voice resquests don't receive a voice response because of the stricter user gesture requirements for autoplay.

### Note: Update for week of Nov. 3, 2025:

Modified the web app to run local:
1. using llama-cpp-python server Qwen2.5-VL-7B, faster-whisper (SST) and piper (TTS)
2. SQLite for memory persistence (no multi-user concurrency required offline)
4. Language, image understanding, and tool calling are working great
4. Podman for containerization

note: this runs surprisingly well on a nine year old I5 with 32GB of RAM, but it can only handle single image processing.

### As of Jan. 2026:

1. Object Detection & Spatial Reasoning 
2. Better consumer hardware
3. Maybe try Qwen2.5-VL-3B
4. Start moving this to embedded hardware / realtime sensing
5. Drive a robot











