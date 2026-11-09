# PaySim feature store

## Checking and choosing the data

To analyze the PaySim CSV file, we used DuckDB, which allows us to run queries without loading everything into pandas. So, we limited the memory usage to 512 megabytes. Using it, we detected customer ID gaps, bad times and amounts, bad labels, and duplicate rows. None of these problems have been detected. We left zero amounts since zero does not necessarily indicate a lack of transaction information.

We randomly chose 400 customers and another 100 customers active at other times. We used a fixed order according to customer ID in order to guarantee that the same data will always give us the same sample. The active customers will help illustrate the changes in features, but they cannot be treated as a representative sample. We have chosen complete histories for the chosen IDs instead of selecting random transaction rows, which can miss earlier history of transactions. So, we got 500 customers and 600 transactions. Then we used pandas for smaller tables.

## Working with time
PaySim provides hours as features and not dates. To convert hours into UTC time, we have used pandas to consider step 1 as January 1, 2025 at 00:00 and add one hour for each subsequent step. This starting date is nothing but a reference for our simulation. Sticking to one timezone helps timestamp comparison.

Transactions of all other steps apart from the current hour are considered to predict for an hour. We have decided so since the PaySim dataset doesn’t provide us with the transaction order for each hour. It would mean that we will be considering information not yet present. We also assume that the hourly feature update will be available at its boundaries without any delay. To ensure that Feast doesn’t provide us with any updates before the availability timestamp, we have considered ten minutes delay also.

## Calculating customer features
With pandas, we aggregated transaction data according to customer and hour and used rolling aggregation to obtain a sum over the last 24 hours for each customer. We obtained four aggregate features: count of transactions, total amount, average amount, and count of money transfers. These aggregate features represent a simple description of recent activity, but we do not prove that these features predict fraud cases. The flag whether transactions were made in the window and fraud labels and balance features are not used to generate these aggregates.

The hours without transactions are filled with zeros to ensure that we use 24 hours instead of 24 transaction records. We update our features once per hour regardless of whether there was any new transaction in order to drop expired transactions from the aggregate values. If we have an old customer with no activity in the window, we will get zeros for all the features except average amount that we will fill with zeros. If we do not have a feature record for the customer, we will get missing values.
## Using Feast


In order to describe the customer entity, the feature source, and the feature view, we used Feast. The customer_id field associates every transaction with its features. In our pandas script, we compute the values, while Feast takes care of the retrieval of the values' historical values and insertion into the online store. We used Parquet for the storage of historical features because it allows for saving tables compactly and preserving the data types. We used SQLite for the online values because it operates locally without having to install any separate database server.

The training dataset asks for features that are available at each timestamp of transactions. The file backend will collapse all duplicate customers/time combinations or remove the rows until the very first feature update. For that reason, we fetch the customer/time combinations separately and associate them with every transaction through a pandas left join. For the online query, we transfer the features up to the selected point in time into SQLite. We impose a two-hour freshness limit in order to refuse old updates. This freshness limit is different from the 24-hour calculation window.

## Checking the results


We first considered a case when the expected answer could be calculated manually. Then we verified our solution against another pandas operation on a filtered version of the initial transactions. This was important since the offline and online value could coincide but still be wrong. Assertions were used to halt the notebook in case of failed validation, while the NumPy comparison allowed for small rounding of the amount. Count and pattern of nulls had to coincide perfectly.

There were no mismatches for all 600 rows in the prediction set with regard to the history validation. In total, for two different times, 7,014 comparisons of raw computation, offline lookup and online access showed no mismatches. Unknown users, exactness of the timestamp, late updating and multiple requests were tested as well. The addition of the future transaction did not affect past values, and the repeated online update did not change anything either. Temporary stores were used to prevent interference from previous notebook runs and deleted after that.

## What we learned


Approximately 99.85% of the senders present in the whole dataset occur only once. Since only 12 of the transactions in our sample have any historical information within the last 24 hours, we expect there to be many missing or null transaction histories. We used matplotlib to demonstrate the customer history distribution to highlight this constraint. Selecting more rows would not help us achieve repeated customer history.

There were also no frauds in our sample; therefore, we did not develop the optional fraud classifier model. It would be erroneous to report the performance of the fraud classifier model in this sample because such a model requires more appropriate data. The correctness of the feature-store workflow was established. Streaming and scaling would require some extra effort.
