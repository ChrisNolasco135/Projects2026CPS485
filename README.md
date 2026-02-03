# Projects2026CPS485
## SQL Smart Database Manager
Webapp that allows users to create and manage SQL databases that utilizes Gemini as the main driver for smart interactions with the database. This allows for easy access and usability for anyone without the requirement of intesive training on SQL and database management. 

This project will utilize a MVC infrastructure which allows for the user to engage with the program at a surface level without the need to consider the computations needed for an easy to use program. 

## Features for Smart Database Manager

- Create or import pre-existing databases
- Modify or search databases utilizing easy to use, customizable written prompts
- Gemini can ask the user for clarification if there’s ambiguities in the prompt before generating the sql
- Visualize the data dynamically using graphs instead of outputting all the rows from the database
- Display the sql generated to the user with an option for Gemini to generate a short explanation of what the sql does.
- Follow up queries on the data possible after output 
- If Gemini writes invalid sql the errors will be fed back to it and it can fix the sql
- Save or export final table results to device or email

Pre-existing database to use:
- Chinook database (digital media store)
  - Has tables for artists, albums, media tracks, invoices
