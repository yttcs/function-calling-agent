## Barebones function calling agent using the following technology: 

1. Backend: FastAPI, SQL Model, OpenAI completions API, Tavily Search API
2. Frontend: Jinja2, Bootstrap, FetchAPI
3. Security: Oauth2 with password flow using JWT bearer tokens and a remote MariaDB user identity database hosted on a DigitalOcean VPS.

This is a work in progress and it's planned to have multiple updates on a weekly basis.

### Update for week of Jun. 30, 2025:

1. Added multiuser capability
2. Added Tavily Extract API
3. Switched from gpt-3.5-turbo to gpt-4o

### Update for week of Jul. 21, 2025:

1. Added text to speech using gpt-4o-mini-tts for completion.choices[0].message.content (that means the agent now has a voice)

### Note: Update for week of Aug. 11, 2025:
1. Addied speech to text using gpt-4o-mini-transcribe and Whisper (this means that there's )
2. Added date tool
3. Added time tool so the model can access UTC time and convert to user requsted time zone.

### Note: Update for week of Oct. 20, 2025:

1. Added database persistence in combination with in-memory python dict
2. Employed a hybrid HTMX/JS solution to play TTS in browser from text and voice requests
3. Added HTMX to avoid full page refreshes
4. Cleaned up UI
5. Containerized with Podman
6. Deployed to AWS ECS/Fargate:  SENTyENT.com

Will refine here and there, but this phase of the project, in the main, is complete.  

### Next Phase:

Take lessons learned from previous phase and apply to off-grid, multi-agent, multi-user, sensor fusion project
1. Fine tune SLM (either phi-4 variant or gpt-oss 20B)
2. Purchase hardware
3. Start making things work together
4. Deploy in the field
5. Create a demonstration video




