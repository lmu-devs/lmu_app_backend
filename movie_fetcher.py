from data_fetcher.src.cinema.crawler.tum_movie_crawler import TumScreeningCrawler

if __name__ == "__main__":
    crawler = TumScreeningCrawler()
    for screening in crawler.crawl():
        print("--------------------------------\n")
        print(screening.__dict__)
    print("Number of screenings: ", len(crawler.crawl()))
