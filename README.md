# DatumEra

This is the public version of DatumEra.

Datum Era is a GenAI based web app that translates different flavours of SQL code to Snowflake SQL.

It was built using prompt engineering, OpenAI API, Flask, Firebase Authentication, Firestore and React. It was originally build to resolve the use case of translating Redshift SQL to Snowflake SQL. It will be expanded to translate between all flavours of SQL.

This tool can be used to help people with database migration. Their SQL statements can be quickly translated to the SQL flavour that their new database uses.

Since I have plans of releasing this web app in the future, the details of the prompt used to generate the translated SQL are not a part of this repo.

### Unbuilt Parts

DatumEra is still a work in process. Here are some features that I intend to add that it does not have:

- Landing page
- Buying individual credits - the UI has been build but the API endpoint to do this has not been built
- Making the translation work for other flavours of SQL
- Intuitive error handling - most of the error handling in the code base is with console.log

### Areas of Improvement

Existing parts of DatumEra can also be improved.

- Scalability. The frontend lacks architecture that allows for new pages and components to be easily added on top. A base class for API requests can be created.
- Efficiency. OpenAI has released a batch API. I need to investigate into this API to see if it can be used. 
