# Summary Comparison

## Introdocution

This repository aims to further clean the scraped data from the BookSum repo (https://github.com/salesforce/booksum) to allow stronger correlation between reviews that should be compared. It focuses on the human written summaries written at the book-level and chapter-level (or as we shall now call: section-level)

Once the data is 'fixed', it is compared with the original booksum data to test the significance of the fixed result. Both datasets are run through various standardized metrics such as rouge, bleu, bart, and more.

Finally, kappa values are calculated to evaluate the level of agreement for all metrics.


## Usage

### 1. Collect results from booksum

our own scraped results can be found, otherwise you can use the booksum repo
- scraped summaries can be found inside scripts folder.
- original text for each book can be found inside all_chapterized_books folder.

some select few results are missing from the original booksum due to failed links or timeouts. (insert number missing from original)

^ honestly pretty big issue.




### 2. 'fix' data
talk about how.

The final result is that 1,756 extra summaries are compared based on their id.


### 3. compare results

talk about how.

talk about our findings.


### 4. perform kappa / kripp alpha calculations

how,

our findings.


### conclusion.

