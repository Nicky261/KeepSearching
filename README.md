# KeepSearching
Project worked on the final of the second semester of second year.

Q:What does the repo contain?
  A: several scripts for learning ws (ws stands for web scraping)

Q:What sripts?
  A: paginOptions -> So you want to find documents on a topic (PDFs in our case). 
                     The script avoids to be blacklisted on se (search engine(s)).
                     With Deeper function you go deeper on links <=> you reperform a sq (search query + site: option <- one of the obtained sites)
    linkExtracter -> you extract all links avaible from a web page
    newsDuck      -> generates a compiled LaTeX document with news on a query on DuckDuckGo. After an email is sent with it
    bagOfWords    -> also for news from DDG. Get freq. of words from paragraphs from the webpages of all obtained links on se.
    fileDownloader-> for downloading PDF in paginOptions
