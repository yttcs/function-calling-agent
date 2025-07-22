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
2. Adding speech to text using gpt-4o-mini-transcribe (this means that users will be able to talk and/or type their queries)
   
note: this hasn't been updated to Git
