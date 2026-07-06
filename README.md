# Flask SSTI Lab

A deliberately vulnerable Flask application created as a cybersecurity training project. The goal is to identify a Server-Side Template Injection (SSTI) flaw in a fictional intelligence portal and retrieve the lab flag.

> [!CAUTION]
> This application intentionally permits template injection and may allow code execution inside its container. Run it only on your own machine, keep it bound to `127.0.0.1`, and never deploy it to a public server or shared network.

The portal, organizations, people, and records shown in the application are fictional. This project is not affiliated with any real institution.

## Learning objectives

- Recognize unsafe use of Jinja's `render_template_string`
- Confirm SSTI with a harmless expression
- Explore the template context and retrieve the lab flag
- Understand why untrusted input must never be treated as a template

## Run with Docker

Docker is the recommended way to run the lab.

```bash
docker build -t flask-ssti-lab .
docker run --rm --read-only --cap-drop=ALL --security-opt=no-new-privileges \
  -p 127.0.0.1:5000:5000 flask-ssti-lab
```

Open `http://127.0.0.1:5000`.

Your first objective is to discover the login credentials from the clues exposed by the application. After signing in, start with the harmless payload `{{ 7 * 7 }}` on the personnel search page. The remaining discovery is intentionally left to the learner.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m flask --app app run
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

## Tests

```bash
python -m pytest
```

The test suite documents the intended vulnerability and checks that unrelated reflected XSS is not introduced.

## Scope

There is exactly one intentional vulnerable sink, marked `INTENTIONALLY VULNERABLE` in `app.py`. Everything else should be treated as ordinary application code and reported if it behaves unexpectedly.

## License

Released under the [MIT License](LICENSE).
