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

note: some select few results are missing from the original booksum due to failed links (mostly pink monkey.)
the number of missed sections is greatly outweighed by the amount of 'fixed' data that now properly corrolates to one another via ID.




### 2. 'fix' data
talk about how.

problems we tried to solve:
- booksum says chapters, but it is better defined as sections, as not all chapterization's from booksum worked.
- roman numerals weren't all fixed.
- aggregates needed to be fixed
- aggregate sections being named differently from one another, dracula chapter 3-4,vs, dracula chapter 3 chapter 4; normalize them.
- issues with titles being for the same book but from different versions
- issues with summaries being for the same book but with different titles, eg. The invisible man, vs, invisible man
- edge case summaries that spanned multiple acts, eg. act-3 scene-3 to act-4 scene-2. hard to tell how many chapters/scenes this section covers.
- issues with books that have prologues / epilogues, some sources include into chapters, some keep separate.
- the aeneid covers multiple books but treats the books as chapters.


go over structure of new jsonl's and what is changed.

The final result is that 1,756 extra summaries are compared based on their id.


### 3. compare results

talk about how.

talk about our findings.


### 4. perform kappa / kripp alpha calculations

how,

our findings.


### conclusion.

nothings any better lol, but hey I tried.