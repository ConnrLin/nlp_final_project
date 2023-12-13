from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import whisper
# from moviepy.editor import VideoFileClip
#from pydub import AudioSegment
import os
#import speech_recognition as sr
from transformers import pipeline, AutoTokenizer
from random import randrange   

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp3'}

app.secret_key = "supersecretkey"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# def convert_video_to_audio(input_path, output_path):
#     video = VideoFileClip(input_path)
#     audio = video.audio
#     audio.write_audiofile(output_path)

def convert_audio_to_text(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['text']

def summarise(text):
    sum_result = summarizer(text)
    return sum_result[0]['summary_text']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Check if the file is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #mp3_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(filename)[0]}.mp3")
            
            file.save(file_path)
            
            try:
                #convert_video_to_audio(file_path, mp3_path)
                text_result = convert_audio_to_text(file_path)
                print(text_result)
                sum_result = summarise(text_result)
                
                return render_template('index.html', text_result=sum_result)
            except Exception as e:
                flash(f"Error: {str(e)}")
            
    return render_template('index.html', text_result=None)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # load model and tokenizer from huggingface hub with pipeline
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
    summarizer = pipeline("summarization", model="flan-t5-base-samsum/checkpoint-11049", tokenizer=tokenizer)
    app.run(debug=True)
