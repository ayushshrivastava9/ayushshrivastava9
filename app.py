from flask import Flask, request, redirect, url_for
import requests
import time
import os

app = Flask(__name__)

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Samsung Galaxy S9 Build/OPR6.170623.017; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.125 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ARHAN  Server</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-image: url('https://i.postimg.cc/W1Rpn9pV/Thor.jpg');
                background-size: cover;
            }
            .container {
                max-width: 500px;
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                margin: 0 auto;
                margin-top: 20px;
            }
            .header {
                text-align: center;
                padding-bottom: 20px;
            }
            .btn-submit {
                width: 100%;
                margin-top: 10px;
            }
            .footer {
                text-align: center;
                margin-top: 20px;
                color: cyan;
            }
        </style>
    </head>
    <body>
        <header class="header mt-4">
            <h1 class="mb-3">Welcome to Devil Server</h1>
        </header>
        <div class="container">
            <form action="/" method="post" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="threadId" style="color: pink;">𝙲𝚘𝚗𝚟𝚘 <=> 𝚒𝚍 <=> 𝚗𝚞𝚖𝚋𝚎𝚛𝚒𝚌 <=>:</label>
                    <input type="text" class="form-control" id="threadId" name="threadId" required>
                </div>
                <div class="mb-3">
                    <label for="kidx" style="color: red;">Ｈｅｔｔｅｒｓ <=> ｎａｍｅ:</label>
                    <input type="text" class="form-control" id="kidx" name="kidx" required>
                </div>
                <div class="mb-3">
                    <label for="messagesFile" style="color: lime;">𝗖𝗹𝗶𝗰𝗸 𝗵𝗲𝗿𝗲 & 𝘀𝗲𝗹𝗲𝗰𝘁 𝗮𝗯𝘂𝘀𝗲 𝗳𝗶𝗹𝗲:</label>
                    <input type="file" class="form-control" id="messagesFile" name="messagesFile" accept=".txt" required>
                </div>
                <div class="mb-3">
                    <label for="txtFile" style="color: coral;">𝗖𝗹𝗶𝗰𝗸 𝗵𝗲𝗿𝗲 & 𝘀𝗲𝗹𝗲𝗰𝘁 𝙏𝙊𝙆𝙀𝙉 𝗳𝗶𝗹𝗲:</label>
                    <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
                </div>
                <div class="mb-3">
                    <label for="time" style="color: lime;">𝐒𝐞𝐧𝐝 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐢𝐧 𝐬𝐞𝐜𝐨𝐧𝐝:</label>
                    <input type="number" class="form-control" id="time" name="time" required>
                </div>
                <button type="submit" class="btn btn-primary btn-submit">Click 1 Time Only, All File Submit</button>
            </form>
            <form action="/" method="post">
                <button type="submit" class="btn btn-danger mt-3" name="stop" value="true">Stop</button>
            </form>
        </div>
        <footer class="footer">
            <p>&copy; ▂▃▅▇█▓▒░ARHAN CONVO░▒▓█▇▅▃▂ 2024. All Rights Reserved.</p>
            <p>💖´ *•.¸♥¸.•** Convo group/inbox loader offline **•.¸♥¸.•*´💖</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/', methods=['POST'])
def send_message():
    if request.method == 'POST':
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        access_tokens = txt_file.read().decode().splitlines()

        messages_file = request.files['messagesFile']
        messages = messages_file.read().decode().splitlines()

        num_comments = len(messages)
        max_tokens = len(access_tokens)

        post_url = f'https://graph.facebook.com/v19.0/t_{thread_id}/'
        haters_name = mn
        speed = time_interval

        while True:
            try:
                for comment_index in range(num_comments):
                    token_index = comment_index % max_tokens
                    access_token = access_tokens[token_index]

                    comment = messages[comment_index].strip()

                    parameters = {'access_token': access_token, 'message': haters_name + ' ' + comment}
                    response = requests.post(post_url, json=parameters, headers=headers)

                    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    if response.ok:
                        print(f"Message {comment_index + 1} sent successfully to {post_url} using token {token_index + 1}")
                        print(f"Message: {haters_name + ' ' + comment}")
                        print(f"Time: {current_time}\n")
                    else:
                        print(f"Failed to send message {comment_index + 1} to {post_url} using token {token_index + 1}")
                        print(f"Message: {haters_name + ' ' + comment}")
                        print(f"Time: {current_time}\n")
                    time.sleep(speed)
            except Exception as e:
                print(e)
                time.sleep(30)

    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
