from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
from PIL import Image

from multiprocessing import Process
from pathlib import Path
import shutil
import traceback
from datetime import datetime
import time
import re
import os
import io

p = print
opt = webdriver.ChromeOptions()
opt.headless = True # run Chrome Driver in headless mode
ua = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"}
engine = "https://duckduckgo.com/lite/?q="  # DuckDuckGo query URL
msee_base = "https://mangasee123.com" # MangaSee URL
msee_dir = f"{msee_base}/directory" # List of all hosted content

root = Path("./Mangas") #i.e. /Users/<username>/Documents/Mangas for UNIX - Default: folder above current directory
quality = 90 # higher quality = larger file size for JPEG (from PNG conversion)

os.chdir(root)

def fetch_page():
    name, raw_href = [], []
    p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) Going to '{msee_dir}'")
    driver.get(msee_dir)
    for a in BeautifulSoup(driver.page_source, "html.parser").find_all("a", href=True):
        name.append(a.text)
        raw_href.append(a["href"])
    mod_href = [i.split("/")[-1].casefold() for i in raw_href]
    mod_name = [j.casefold() for j in name]
    return name, mod_name, raw_href, mod_href

def get_input(t, mt, mh):
    user_query = input("\n\nEnter content to search for: ")
    term = user_query.casefold().split(" ")
    t_match = [mt.index(i) for i in mt if any(j in i for j in term)]
    h_match = [mh.index(i) for i in mh if any(j in i for j in term)]
    for i in h_match:
        if i not in t_match: t_match.append(i)
    l = len(t_match)
    p(f"\n\nMatch(es) for '{user_query}':")
    for i in range(l):
        index = t_match[i]
        p(f"{i+1}) {t[index]}")
    confirm_query = input(f"\n\nIs your choice here? (Default: No) [N/Y/[1-{l}]]: ").casefold() or "n"
    if "y" in confirm_query:
        num_sel = input(f"\n\nWhich number? (Default: 1) [1-{l}]: ") or "1"
        try:
            indx = t_match[int(num_sel)-1]
            p(f"\n\n'{t[indx]}' chosen... ")
            return indx
        except ValueError:
            p("\n\nThat doesn't seem to be a valid choice")
            return get_input(t, mt, mh)
    try:
        choice = int(confirm_query)
        if choice in list(range(1, l+1)):
            idx = t_match[choice-1]
            p(f"\n\n'{t[idx]}' chosen")
            return idx
        else:
            p(f"\n\nThat doesn't seem to be in the range of matches given")
            return get_input(t, mt, mh)
    except ValueError:
        p("\n\nThat doesn't seem to be a valid number")
        return get_input(t, mt, mh)
    else:
        p("\n\nLet's try again")
        return get_input(t, mt, mh)

def get_content_page(c):
    p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) Going to '{c}'")
    driver.get(c)
    title = driver.title.split("|")[0].strip()
    b = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "ShowAllChapters"))).click()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    latest_chapter = soup.find("span", class_="ng-binding", style=lambda s: s and "font-weight:600" in s).text.strip().split()[-1]
    p(f"{datetime.now().strftime('%H:%M:%S')}) Searching for all chapters of '{title}'")
    container_pages = [f"{msee_base}{a['href']}" for a in soup.find_all("a", class_="list-group-item ChapterLink ng-scope", href=True)]
    return container_pages, latest_chapter, title

def scraper(array_chapter, lc, t, s=root, q=quality):
    img, endings, root_storage = [], (".png", ".jpg", ".jpeg"), s / t
    if not root_storage.is_dir():
        root_storage.mkdir(parents=True, exist_ok=True)
    p(f"{datetime.now().strftime('%H:%M:%S')}) Creating the '{root_storage}' directory\n\n")
    for chapter in array_chapter:
        driver.get(chapter)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for i in soup.find_all("img"):
            image_src = i["src"]
            if image_src.startswith("https") and image_src.endswith(endings):
                    img.append(image_src)
                    p(f"{datetime.now().strftime('%H:%M:%S')}) Adding {image_src.split('/')[-1]}! ", end="\r")
    nd_img = list(dict.fromkeys(img))
    file_download(nd_img, root_storage)
    p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) Done downloading '{t}'!\n\n")
    return root_storage

def file_download(images, dir, q=quality):
    image_len = len(images)
    current = [j[-1] for j in [i.split("/") for i in images]]
    cc = [float(k.split("-")[0].lstrip("0")) for k in current]
    cp = [float(k.split("-")[-1].lstrip("0").split(".")[0]) for k in current]
    for page in range(image_len):
        chapter_root = dir / f"Chapter {cc[page]:g}"
        chapter_root.mkdir(parents=True, exist_ok=True)
        loc = chapter_root / f"{current[page].split('.')[0]}.jpeg"
        if not loc.is_file():
            img = Image.open(io.BytesIO(requests.get(images[page]).content))
            if img.mode != "RGB": img = img.convert("RGB")
            img.save(loc, optimize=True, quality=q)
            p(f"Progress: [Chapter {cc[page]:g}/{cc[-1]:g}]: {100*cp[page]/cp[-1]:g}% ", end="\r")

def get_search_engine_query(content_title):
        query = f"{content_title} Wiki - Fandom"
        # convert search term + specifics' string to URL encoding
        search_url = f"{engine}{requests.utils.quote(query)}"
        p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) Sending '{query}' to search engine")
        # sends user agent header for: Chrome 99.0 on Windows 10
        r = requests.get(search_url, headers=ua)
        soup = BeautifulSoup(r.text, "html.parser")
        probable_link = soup.find_all("a", class_="result-link", href=True)
        for i in probable_link:
            link_title = i.text
            if link_title.count("|") == 1 and "Wiki | Fandom" in link_title: return i["href"]

def get_wiki_page(wiki_page):
    p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) Searching for relevant section on wiki page")
    r = requests.get(wiki_page, headers=ua)
    soup = BeautifulSoup(r.text, "html.parser")
    matches = [link["href"] for link in soup.find_all("a", href=True) if ("volumes" or "chapters") in (link["href"] or link.string).casefold()]
    if matches:
        return matches[0]
    else:
        p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) Non-regular layout, restarting browser for semi-manual sorting")
        return wiki_page

def mini_cleanup_reg(v_search, tb, v_arr, c_arr):
    v_arr.append(v_search.text.split(" ")[-1]) ########### CHECK IF CONVERTING TO NORMAL FOR LOOP IS FASTER
    c_arr.append([re.split(".\s|:\s|;\s|st\s|nd\s|rd\s", j.text)[0].lstrip("0").lstrip("-") for j in [i for i in tb.find_all("li")] if j.text[0].isdigit()])
    return v_arr, c_arr

def get_wiki_table(wiki_content_section, title):
    volumes_array, chapters_array = [], []
    p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) Searching for contents' info table\n\n")
    r = requests.get(wiki_content_section)
    soup = BeautifulSoup(r.text, "html.parser")
    for tbody in soup.find_all("tbody"):
        vol_num = tbody.find("span", id=lambda value: value and value.casefold().startswith("volume_"))
        if vol_num is not None:
            volumes, chapters = mini_cleanup_reg(vol_num, tbody, volumes_array, chapters_array)
        else:
            vol_num = tbody.find("a", title=lambda value: value and value.casefold().startswith("volume_"))
            if vol_num is not None: volumes, chapters = mini_cleanup_reg(vol_num, tbody, volumes_array, chapters_array)
    first_vol = str(volumes[0])
    if first_vol != title.split(" ")[-1]:
        del volumes[0]
        del chapters[0]
    else:
        del volumes[1:]
        del chapters[1:]
    
    return volumes, [i for i in chapters if i]

def get_man_list(driver, wiki_page):
    starting_chapter, aux_chapters, chapters = 1, [], []
    opt.headless = False  # run Chrome Driver in visible mode
    driver.quit()
    driver = webdriver.Chrome(options=opt)
    driver.delete_all_cookies()
    driver.get(wiki_page)
    p("Once chapter list table manually located...")
    p("1) <Enter> total number of officially released volumes")
    p("2) <Enter> the ending chapter number for each respective volume (DON'T INCLUDE SIDE CHAPTERS WITH DECIMALS)")
    p("Leave an empty field or non-numeric value to finish chapter entry")
    volumes = list(range(1, int(input("\n\nEnter total number of officially released volumes: "))+1))
    for i in range(len(volumes)):
        ending_chapter = input(f"Enter ending chapter for 'Volume {volumes[i]}': ")
        if str(ending_chapter).isnumeric():
            aux_chapters.append(ending_chapter)
        else:
            p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) DONE CHAPTER ENTRY")
    for i in range(len(volumes)):
        chapters.append(list(range(starting_chapter, aux_chapters[i])))
        starting_chapter = aux_chapters[i]+1
    return volumes, chapters

def sort_main_chapters(content_dir, volume_list, chapter_list):
    for i in range(len(chapter_list)):
        vol_str = f"Volume {volume_list[i]}"
        vol_dir = content_dir / Path(vol_str)
        vol_dir.mkdir(parents=True, exist_ok=True)
        for j in chapter_list[i]:
            chap_str = f"Chapter {j}"
            chap_dir = Path(chap_str)
            old_chap_folder = content_dir / chap_dir
            new_chap_folder = vol_dir / chap_dir
            p(f"{datetime.now().strftime('%H:%M:%S')}) Sorting '{chap_str}' into '{vol_str}' ", end="\r")
            shutil.move(old_chap_folder, new_chap_folder)

def sort_side_chapters(content_dir, volume_list, chapter_list):
    src_chapter, dst_chapter, vol_num = [], [], []
    p(f"\n\n\n{datetime.now().strftime('%H:%M:%S')}) Sorting side chapters into their parent volumes (if any)")
    for i in content_dir.iterdir():
        if i.suffix != "" and i.is_dir():
            child_chapter = i.name
            src_chapter.append(content_dir / child_chapter)
            parent_chapter = child_chapter.split(".")[0]
            for j in content_dir.glob("*/" + parent_chapter):
                vol_parent = j.parent
                dst_chapter.append(content_dir / vol_parent / child_chapter)
    for k in range(len(src_chapter)):
        shutil.move(src_chapter[k], dst_chapter[k])

    p(f"\n{datetime.now().strftime('%H:%M:%S')}) Sorting chapters not in tankōbon format (if any)")
    if len(volume_list) != len(chapter_list):
        vol_dir = content_dir / Path(f"Volume {volume_list[-1]}")
    else:
        vol_num = [int(m.name.split(" ")[-1]) for m in content_dir.iterdir() if m.name.startswith("Volume")]
        vol_num.sort()
        vol_dir = content_dir / Path(f"Volume {vol_num[-1]+1}")
    for l in content_dir.iterdir():
        chapter_name = l.name
        if l.is_dir() and not chapter_name.startswith("Volume"): shutil.move(l, vol_dir / chapter_name)

def main(driver):
    title, modified_title, href_link, modified_href = fetch_page()
    link = f"{msee_base}{href_link[int(get_input(title, modified_title, modified_href))]}"
    array_chapter, latest_chapter, page_title = get_content_page(link)
    dir = scraper(array_chapter, float(latest_chapter), page_title)
    wiki_url = get_search_engine_query(page_title)
    info_table_page = get_wiki_page(wiki_url)
    if info_table_page == wiki_url:
        volume_list, chapter_list = get_man_list(driver, info_table_page)
    else:
        volume_list, chapter_list = get_wiki_table(info_table_page, page_title)
    sort_main_chapters(dir, volume_list, chapter_list)
    sort_side_chapters(dir, volume_list, chapter_list)

if __name__ == "__main__":
    p("\n\n=== Shiro-oni START ===")
    start = time.time()
    p(f"\n{datetime.now().strftime('%H:%M:%S')}) Opening headless browser")
    driver = webdriver.Chrome(options=opt)
    driver.delete_all_cookies()
    try:
        main(driver)
    except KeyboardInterrupt as ki:
        p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) Interrupted!\n\n{ki}\n\n")
    except Exception as e:
        p(traceback.format_exc())
        p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) Error!\n\n{e}\n\n")
    p(f"\n\n{datetime.now().strftime('%H:%M:%S')}) Closing headless browser\n")
    driver.quit()
    end = time.time()
    p(f"\n\n\nAll operations completed in: ~{int(end - start)} seconds!")
    p("=== Shiro-oni END ===\n\n")