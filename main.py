from openai import AsyncOpenAI
import httpx
import os
import io
from scipy.io import wavfile
import numpy as np
from typing import Annotated
from fastapi import FastAPI, Response, Form, Depends, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import select
from mangum import Mangum

from db import *
from models import *
from tools import *

# import asyncio
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()

openai = AsyncOpenAI()

OPENAI_API_SECRET_KEY = os.getenv('OPENAI_API__KEY')
client = AsyncOpenAI(api_key=OPENAI_API_SECRET_KEY)

app = FastAPI()

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/token")
db_dependency = Depends(get_session)  # this is our database session dependency injection
user_dependency = Annotated[dict, Depends(get_current_user)]  # this is our JWT decoder dependency injection

handler = Mangum(app) # AWS expects a handler to hookup on to run our app
templates = Jinja2Templates(directory="templates")

# -------------------------------------------------------------------------------------
# Here is the /token endpoint that calls the two authentication functions in models.py
# -------------------------------------------------------------------------------------
@app.post("/token")
def login_for_access_token(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = db_dependency):
    user = authenticate_user(form_data.username, form_data.password, session)   # authenticate_user function
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)   # create_access_token function

    response.set_cookie(key='access_token', value=token, httponly=True)     # put the JWt token in the browser
    return True

# User will not be able to access a secured resource endpoint until they are
# 1. authenticated and issued a token by login_for_access_token (above)
# 2. have that token decoded at the endpoint they are trying to access by the get_current_user function (below).
#    This token decoding process takes place at every endpoint

# Authentication Process:
#     1. login_for_access_token calls authenticate_user and create_access_token.
#     2. this results in a JWT access token being place in the user's browser.
#     3. when the user tries to access a secured endpoint, the endpoint function
#        will call get_current_user to decode the JWT access token in the user's browser
#        to compare it to the issuing backend.

# ----------------------------------------------------------------
# Register a new user in the DB. These endpoints don't get secured
# ----------------------------------------------------------------
@app.get("/create/user", response_class=HTMLResponse)
def registration_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
def register_user(request: Request, email: str = Form(...), username: str = Form(...),
                        full_name: str = Form(...), password: str = Form(...), password2: str = Form(...),
                        session: Session = db_dependency):

    validation1 = session.query(User).filter(User.username == username).first()
    validation2 = session.query(User).filter(User.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid registration request"
        context = {"request": request, "msg": msg}
        return templates.TemplateResponse("register.html", context)

    user_model = User()
    user_model.username = username
    user_model.email = email
    user_model.full_name = full_name

    hash_password = get_password_hash(password)

    user_model.hashed_password = hash_password
    user_model.is_active = True

    session.add(user_model)
    session.commit()

    msg = "User successfully created"
    context = {"request": request, "msg": msg}
    return templates.TemplateResponse("login.html", context)


# -----------------------------------------------------
# root - deletes cookie and redirects to the login page
# -----------------------------------------------------
@app.get("/")
def redirect_logout():

    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token") # if there's a JWT in the browser, delete it.
# Authentication and Login Endpoints. These endpoints don't get secured.
    return response


# -----
# Login
# -----
@app.get("/login", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, session: Session = db_dependency):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/chat", status_code=status.HTTP_302_FOUND)

        # this variable gets its value from "/token"
        validate_user_cookie = login_for_access_token(response=response, form_data=form, session=session)

        if not validate_user_cookie:
            msg = "cookie not validated"
            context={"request": request, "msg": msg}
            return templates.TemplateResponse("login.html", context)
        return response
    except HTTPException:
        msg = "Username or Password incorrect"
        context = {"request": request, "msg": msg}
        return templates.TemplateResponse("login.html", context)

# ----------
# Exceptions
# ----------

def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception

def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response

# ---------
# Logout
# ---------

@app.get("/logout")
def logout(request: Request):
    msg = "Logout Successful"
    context = {"request": request, "msg": msg}
    response = templates.TemplateResponse("login.html", context)
    response.delete_cookie(key="access_token")
    return response


# -----------
# Delete User
# -----------
@app.get("/delete_user", response_class=HTMLResponse)
def delete_user_page(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("delete_user.html", context)


@app.post("/delete_user", response_class=HTMLResponse)
def delete_user(request: Request, username: str=Form(...), email: str=Form(...),
                      session: Session = db_dependency):

    try:
        statement = select(User).where(User.username == username).where(User.email == email)
        user_to_delete = session.scalars(statement).one()

        # convert sqlalchemy Row to a python dict so we can test form data against DB entries
        # An _sa_instance_state key is added and needs to be deleted
        result = dict(user_to_delete)
        test = result
        del test["_sa_instance_state"]

        session.delete(user_to_delete)
        session.commit()
        msg = "User deleted successfully", test["username"], username  # form data and DB data are matching up
        context = {"request": request, "msg": msg}
        return templates.TemplateResponse("login.html", context)

    except Exception as e:
        # Handle other exceptions (database errors, commit issues, etc.)
        msg = (f"An unexpected error occurred: {e}")
        session.rollback()  # Ensure rollback if an error occurs

        context = {"request": request, "msg": msg}
        return templates.TemplateResponse("delete_user.html", context)


# ---------------------------------------------------------------------------------------------------
# Setting up memory and sessions with dictionaries 
# ---------------------------------------------------------------------------------------------------
chat_sessions = {}
chat_responses = {}
system_prompt = {
    "role": "system",
    "content": 'Your primary job is as a Python and FastAPI coding expert, specializing in multiuser applicastions.'
}

# --------------------------
# Secured Resource Endpoints
# --------------------------

# LLM ---------
@app.get("/chat", response_class=HTMLResponse)
def chat_page(user: user_dependency, request: Request):
    if user:
        chat_id = user.get('id')
        if chat_id not in chat_sessions:
            chat_sessions[chat_id] = []
            chat_responses[chat_id] = []
            chat_sessions[chat_id].append(system_prompt)

        msg = "chat_id", chat_id
        context = {"request": request, 'chat_responses': chat_responses[chat_id], "msg": msg}
        return templates.TemplateResponse("home.html", context)
    else:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.post("/chat", response_class=HTMLResponse)
async def chat(user: user_dependency, request: Request, user_input: Annotated[str, Form()], temperature: float = Form(...), chat_id: Optional[int] = Form(None)):

    if user:
        chat_id = user.get('id')

    if chat_id:

        chat_sessions[chat_id].append({'role': 'user', 'content': user_input})
        chat_responses[chat_id].append(user_input)

    if chat_id is None:
        return HTMLResponse(content="User ID not found.", status_code=400)


    # We're going to get an LLM response or a tool call
    completion = await client.chat.completions.create(
        #model="gpt-3.5-turbo",
        model="gpt-4o",
        messages=chat_sessions[chat_id],
        stream=False,
        temperature=temperature,
        tools=tools,
        tool_choice="auto",
        max_tokens=750
    )

    # Test for tool call(s) and iterate through a list of them to execute the corresponding function based on name.
    if completion.choices[0].message.tool_calls:
        try:
            for tool_call in completion.choices[0].message.tool_calls:
                if function_to_call := available_functions.get(tool_call.function.name):
                    args = json.loads(tool_call.function.arguments)
                    output = function_to_call(**args)

            # provide the LLM's function call back to LLM through the chat history
            chat_sessions[chat_id].append(completion.choices[0].message)

            # provide the function execution result back to the LLM through the chat history
            chat_sessions[chat_id].append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": str(output),
                }
            )

        except Exception as e:

            msg = f"An unexpected error occurred: {e}"
            return templates.TemplateResponse("home.html", {'request': request, "chat_responses": chat_responses[chat_id],"msg": msg})


        # Get the final LLM response
        completion2 = await client.chat.completions.create(
            #model="gpt-3.5-turbo",
            model="gpt-4o",
            messages=chat_sessions[chat_id],
            stream=False,
            temperature=temperature,
            tools=tools,
            tool_choice="auto",
            max_tokens=3250
        )



        # return the final LLM response to the user
        ai_response = completion2.choices[0].message.content
        chat_sessions[chat_id].append({'role': 'assistant', 'content': ai_response})
        chat_responses[chat_id].append(ai_response)


        # convert the tool call response to voice
        async with openai.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=ai_response,
                instructions="Speak in a professional and kind tone.",
                response_format="pcm",
        ) as response:
            await LocalAudioPlayer().play(response)

        msg = "chat_id", chat_id

        return templates.TemplateResponse("home.html", {'request': request, "chat_responses": chat_responses[chat_id], "msg": msg})

    else:

        ai_response = completion.choices[0].message.content
        chat_sessions[chat_id].append({'role': 'assistant', 'content': ai_response})
        chat_responses[chat_id].append(ai_response)

        async with openai.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=ai_response,
                instructions="Speak in a professional and kind tone.",
                response_format="pcm",
        ) as response:
            await LocalAudioPlayer().play(response)

        msg = "chat_id", chat_id, "chat_responses", chat_responses[chat_id]

        return templates.TemplateResponse("home.html", {'request': request, "chat_responses": chat_responses[chat_id], "msg": msg})


# ----------------------
# Transcription Endpoint
# ----------------------
@app.post("/transcribe/")
async def transcribe_audio(user: user_dependency, file: UploadFile = File(...)):

    if user:
        chat_id = user.get('id')

    if chat_id is None:
        return HTMLResponse(content="User ID not found.", status_code=400)

    blob = await file.read()
    buffer = io.BytesIO(blob)
    buffer.name = file.filename

    transcription = await client.audio.transcriptions.create(
       # model="gpt-4o-transcribe",
       model="whisper-1",
       file=buffer
    )

    # save the transcribed audio

    save_path = "transcriptions"
    os.makedirs(save_path, exist_ok=True)
    file_path = os.path.join(save_path, f"{file.filename}.txt")
    with open(file_path, "w") as f:
       f.write(f"ID: {chat_id} - {transcription.text}\n")

    # Internal call to the /chat API

    timeout_config = httpx.Timeout(90.0)
    async with httpx.AsyncClient() as internal_call:
        await internal_call.post("http://localhost:8000/chat", data={"user_input": transcription.text, "temperature": 0.0, "chat_id": chat_id}, timeout = timeout_config)


 # -------------
# DALL-E
# -------------
@app.get("/image", response_class=HTMLResponse)
def image_page(user: user_dependency, request: Request):

    if user:

        return templates.TemplateResponse("image.html", {'request': request})
    else:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.post("/image", response_class=HTMLResponse)
def create_image(request: Request, user_input: Annotated[str, Form()]):
    response = client.images.generate(
        prompt=user_input,
        n=1,
        size='512x512'
    )

    image_url = response.data[0].url
    return templates.TemplateResponse("image.html", {'request': request, 'image_url': image_url})

# --------------------------------------------
# Clear chat log and chat window using fetch()
# --------------------------------------------
@app.post("/clear_memory")
def clear_memory(user:user_dependency):
    chat_id = user.get('id')
    chat_sessions[chat_id].clear()
    return {"message": "Memory cleared successfully"}

@app.post("/clear_template")
def clear_template(user:user_dependency):
    chat_id = user.get('id')
    chat_responses[chat_id].clear()
    return {"message": "Template cleared successfully"}
