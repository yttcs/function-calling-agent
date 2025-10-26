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

Will refine here and there, but this phase of the project, in the main, is complete.  

### Next Phase:

Take lessons learned from previous phase and apply to off-grid, multi-agent, multi-user, sensor fusion project
1. Fine tune SLM (either phi-4 variant or gpt-oss 20B)
2. Purchase hardware
3. Start making things work together
4. Deploy in the field
5. Create a demonstration video





