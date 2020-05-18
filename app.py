from flask import Flask

app = Flask("Optical Braille Recognition Demo")

@app.route('/')
def index():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
