import json
import scrapy

class LinkedCompanySpider(scrapy.Spider):
    name = "linkedin_company_profile"

    # Add your own list of company URLs here
    company_pages = [
        'https://www.linkedin.com/company/gojek?trk=public_jobs_jserp-result_job-search-card-subtitle',
        'https://www.linkedin.com/company/shopee?trk=public_jobs_jserp-result_job-search-card-subtitle'
    ]

    custom_settings = {
        'FEEDS': {'data/%(name)s_%(time)s.jsonl': {'format': 'jsonlines'}},
    }

    def start_requests(self):
        company_index_tracker = 0

        # Uncomment below if reading the company URLs from a file instead of the self.company_pages array
        # self.readUrlsFromJobsFile()

        first_url = self.company_pages[company_index_tracker]

        yield scrapy.Request(url=first_url, callback=self.parse_response, meta={'company_index_tracker': company_index_tracker})

    def parse_response(self, response):
        company_index_tracker = response.meta['company_index_tracker']
        print('***************')
        print('****** Scraping page ' + str(company_index_tracker + 1) + ' of ' + str(len(self.company_pages)))
        print('***************')

        company_item = {}

        company_item['name'] = response.css('.top-card-layout__entity-info h1::text').get(default='not-found').strip()
        company_item['summary'] = response.css('.top-card-layout__entity-info h4 span::text').get(default='not-found').strip()

        try:
            # All company details
            company_details = response.css('.core-section-container__content .mb-2')

            # Industry line
            company_industry_line = company_details[1].css('.text-md::text').getall()
            company_item['industry'] = company_industry_line[1].strip()

            # Company size line
            company_size_line = company_details[2].css('.text-md::text').getall()
            company_item['size'] = company_size_line[1].strip()

            # Company founded
            company_size_line = company_details[5].css('.text-md::text').getall()
            company_item['founded'] = company_size_line[1].strip()
        except IndexError:
            print("Error: Skipped Company - Some details missing")

        yield company_item

        company_index_tracker = company_index_tracker + 1

        if company_index_tracker <= (len(self.company_pages) - 1):
            next_url = self.company_pages[company_index_tracker]

            yield scrapy.Request(url=next_url, callback=self.parse_response, meta={'company_index_tracker': company_index_tracker})

    def readUrlsFromJobsFile(self):
        self.company_pages = []
        with open('jobs.json') as file:
            jobsFromFile = json.load(file)

            for job in jobsFromFile:
                if job['company_link'] != 'not-found':
                    self.company_pages.append(job['company_link'])

        # Remove any duplicate links to prevent the spider from shutting down on duplicates
        self.company_pages = list(set(self.company_pages))
