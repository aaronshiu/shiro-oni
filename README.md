# shiro-oni
 MangaSee content scraper via selenium (homage to HakuNeko + educational attempt at some concepts)
 
 Something along the lines of scraping for data online, downloading content, an attempt at organising chapters into volumes where the first chapter for each volume (usually) is the cover art for the respective volume, so something like an e-reader (Kindle) can display a volume with its cover art properly and then the entire content directory can be forwarded to KindleComicConverter or similar software to optimise for device-specific reading and adding/editing meta-data.

## Outline
1) Install requirements via ```pip install -r requirements.txt``` and launch program: ```python main.py``` [Dependant on Python versions installed on system]
2) Search for content title, input index number and confirm selection.
3) Links to content chapters should take a short while to populate an array for downloading.
4) Majority of time will be spent downloading the content into a subdirectory in the root download directory.
5) Chapters in each volume (if any) should be quantified by searching on DuckDuckGo for fandom website chapter list tables.
6) If this fails from non-standard websites, semi-manual sorting of chapters will commence as browser is relaunched in visible-mode.
7) Root download directory can be changed on ```line 19``` and quality of JPEG downloads can be adjusted from default (```90```) on ```line 33```.

## Common errors
Installing Google Chrome via widely-used package managers should fix Chrome binary not being found:
- MacOS: ```brew install google-chrome``` (Homebrew) [Tested]
- Windows: ```choco install googlechrome``` (Chocolatey)
- Linux: ```sudo apt install chrome-browser``` (APT)

#### Features to implement (possibly)
- Directory archival.
- Testing whether modifying multiple ```mini_cleanup_reg()``` function calls into a single for loop is more efficient.
- Enabling selenium use with other browser binaries i.e. chromium, firefox.
- Splitting single file into multiple files for modular development of whole program.
- Skipping Google Chrome installation (external) necessity for selenium to work.
- Allow more fandom website layouts to be scraped for chapter list tables and/or optional caching user-input chapter list data so future users can skip semi-manual chapter input.
- Convert selenium-based solution into a requests-based (or similar) solution, optimising resource-use/speed [current issues involve not being able to parse Javascript effectively with BeautifulSoup, instead relying on regex/string manipulation].

#### This is merely a fun project and not affiliated in any way with HakuNeko nor the content host. If you enjoy a piece of content, do support local brick-and-mortar stores by purchasing it through them or if not possible, support the original author(s)/writer(s) through official channels.
