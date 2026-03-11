# Student ML Leaderboard

Streamlit app for classroom competitions.

Students upload CSV predictions and a live leaderboard updates automatically.

## CSV Format

id,prediction
1,0
2,1
3,0

prediction must be 0 or 1.

## Run the app

pip install -r requirements.txt
streamlit run app.py

## Hidden Labels

Place a file named:

hidden_test_labels.csv

Format:

id,label
1,0
2,1
3,0

Keep this file private.