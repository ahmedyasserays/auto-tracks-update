from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from time import sleep
from pytube import YouTube
import moviepy.editor as mp
import os
import re


def download(song, path):
  YouTube(song).streams.filter(
      only_audio=True).first().download(output_path=path)


folder = r'D:\music from AYS\python downloaded'

# read files to mark the channels and the owned tracks
with open("Channels", "r") as ch_file:
  channels = ch_file.readlines()

with open("Tracks", "r") as trck_file:
  tracks = trck_file.read().splitlines()


driver = webdriver.Chrome()  # init the chrome driver
for channel in channels:  # loop over the channels
  driver.get(channel)
  singer = driver.find_element_by_class_name('ytd-channel-name').text
  print(singer)
  tgt_folder = folder + '\\' + singer
  if not os.path.exists(tgt_folder):
    os.mkdir(tgt_folder)
  driver.find_element_by_xpath('//*[@id="tabsContent"]/paper-tab[2]/div').click()
  sleep(1)

  for i in range(100):   # proceed to the bottom of the page
    driver.find_element_by_tag_name("html").send_keys(Keys.END)

    videos = driver.find_elements_by_id('video-title')
    for video in videos:
      with open("Tracks", "a") as trck_file:   # downloading new videos
        attempts = 0
        while attempts <= 2:
          try:
            song_link = video.get_attribute("href")
            song_name = video.text
          except StaleElementReferenceException:
            sleep(2)
            attempts += 1
          else:
            if song_link and song_link not in tracks:
              print(f'downloading {song_name} from {song_link}')
              download(song_link, tgt_folder)
              trck_file.write(song_link+'\n')

              # convert to mp3
              temp = []
              for x in song_name:
                if x in ['|', '.', ':']:
                  continue
                else:
                  temp.append(x)
              name = ''.join(temp)
              full_path = os.path.join(tgt_folder, name + '.mp4')
              output_path = os.path.join(tgt_folder, name + '.mp3')
              try:
                clip = mp.AudioFileClip(full_path).subclip(
                  10, )  # disable if do not want any clipping
                clip.write_audiofile(output_path)

                # delete the mp4 file
                if os.path.isfile(full_path) and os.path.isfile(output_path):
                  os.remove(full_path)

              except OSError:
                print("error while trying to convert to mp3")

  # make sure that all files are converted
  mp4_names = os.listdir(tgt_folder)
  for name in mp4_names:  # create audio files from the videos
    if re.search('mp4', name):
      full_path = os.path.join(tgt_folder, name)
      output_path = os.path.join(
        tgt_folder, os.path.splitext(name)[0] + '.mp3')
      clip = mp.AudioFileClip(full_path).subclip(
        10, )  # disable if do not want any clipping
      clip.write_audiofile(output_path)

  # make sure that all videos are deleted
  files = [x[:-3] for x in os.listdir(tgt_folder)]
  for file in files:
    if files.count(file) > 1:
      try:
        os.remove(tgt_folder + '\\' + file + 'mp4')
      except FileNotFoundError:
        pass
  sleep(5)

driver.quit()
