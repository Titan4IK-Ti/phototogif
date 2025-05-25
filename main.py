import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import telebot
from moviepy import VideoFileClip
import tempfile
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Укажите ваш токен бота
bot = telebot.TeleBot('')

# Ваш GIPHY API-ключ
GIPHY_API_KEY = '' 

def upload_to_giphy(gif_path):
    """Загружает GIF на GIPHY и возвращает URL."""
    url = 'https://upload.giphy.com/v1/gifs'
    with open(gif_path, 'rb') as gif_file:
        files = {'file': gif_file}
        data = {'api_key': GIPHY_API_KEY}
        response = requests.post(url, data=data, files=files)
        
        if response.status_code == 200:
            gif_id = response.json()['data']['id']
            return f'https://giphy.com/gifs/{gif_id}'
        else:
            raise Exception(f"Ошибка загрузки на GIPHY: {response.text}")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_suffix = str(message.message_id)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_photo:
            temp_photo.write(downloaded_file)
            temp_photo_path = temp_photo.name
        
        img = Image.open(temp_photo_path)
        width, height = img.size
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            video_path = temp_video.name
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(video_path, fourcc, 1, (width, height))
            
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            video.write(img_cv)
            video.write(img_cv)
            video.release()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.gif') as temp_gif:
            gif_path = temp_gif.name
            clip = VideoFileClip(video_path)
            clip.write_gif(gif_path, fps=1)

        markup = None

        # Попытка загрузить на GIPHY, только если есть API ключ
        if GIPHY_API_KEY:
            try:
                giphy_url = upload_to_giphy(gif_path)
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("без шакальности", url=giphy_url))
            except Exception as giphy_error:
                print(f"[!] Не удалось загрузить на GIPHY: {giphy_error}")

        # Отправляем GIF как анимацию (с кнопкой, если она есть)
        with open(gif_path, 'rb') as gif_file:
            bot.send_animation(message.chat.id, gif_file, reply_markup=markup)
        
        os.remove(temp_photo_path)
        os.remove(video_path)
        os.remove(gif_path)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        text = message.text.strip()
        if len(text) > 32:
            bot.reply_to(message, "Сообщение слишком длинное! Максимум 32 символа.")
            return
        
        file_suffix = str(message.message_id)
        
        background_path = os.path.join(os.getcwd(), 'fon.jpg')
        img = Image.open(background_path).convert('RGB')
        
        if img.size != (300, 100):
            img = img.resize((300, 100), Image.Resampling.LANCZOS)
        
        d = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("Oswald.ttf", 26)
        except:
            font = ImageFont.load_default()
        
        # Рисуем текст в центре изображения
        text_bbox = d.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (300 - text_width) // 2
        y = (80 - text_height) // 2
        d.text((x, y), text, fill=(0, 0, 0), font=font)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_photo:
            temp_photo_path = temp_photo.name
            img.save(temp_photo_path)
        
        width, height = img.size
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            video_path = temp_video.name
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(video_path, fourcc, 1, (width, height))
            
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            video.write(img_cv)
            video.write(img_cv)
            video.release()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.gif') as temp_gif:
            gif_path = temp_gif.name
            clip = VideoFileClip(video_path)
            clip.write_gif(gif_path, fps=1)
        
        with open(gif_path, 'rb') as gif_file:
            bot.send_animation(message.chat.id, gif_file)
        
        os.remove(temp_photo_path)
        os.remove(video_path)
        os.remove(gif_path)
        
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")


def main():
    print("d")
    bot.polling()

if __name__ == "__main__":
    main()
