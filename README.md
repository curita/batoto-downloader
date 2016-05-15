# batoto-downloader
Scrapy spider to download manga series from Batoto

## Usage
```
scrapy runspider batoto.py -a id=ebd831e1d660b0fc -s IMAGES_STORE=/Users/julia/Downloads
```

* `id` is the manga id from bato.to that's going to be downloaded. It's the code after the `#` symbol and before any `_` in Batoto's reader urls of its chapters: `http://bato.to/reader#ebd831e1d660b0fc_2`
* `IMAGES_STORE` is your desired download path
