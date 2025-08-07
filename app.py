from flask import Flask, render_template, request, redirect, url_for, flash, session
import pickle
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = '287ebfa48e422ae4c4037d864993f1a599be4b0928a79c38089ac16c24f2226b'

# Load data with error handling
try:
    popular_df = pickle.load(open('popular.pkl', 'rb'))
    pt = pickle.load(open('pt.pkl', 'rb'))
    books = pickle.load(open('books.pkl', 'rb'))
    similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))
except Exception as e:
    print(f"Error loading data files: {e}")
    popular_df = pd.DataFrame(columns=['Book-Title', 'Book-Author', 'Image-URL-M', 'num_ratings', 'avg_rating'])
    pt = pd.DataFrame()
    books = pd.DataFrame()
    similarity_scores = np.array([])

@app.route('/')
def index():
    current_year = datetime.now().year
    return render_template('index.html',
                         book_name=list(popular_df['Book-Title'].values),
                         author=list(popular_df['Book-Author'].values),
                         image=list(popular_df['Image-URL-M'].values),
                         votes=list(popular_df['num_ratings'].values),
                         rating=list(popular_df['avg_rating'].values),
                         current_year=current_year)

@app.route('/recommend')
def recommend_ui():
    current_year = datetime.now().year
    return render_template('recommend.html', current_year=current_year)

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    if not user_input:
        flash('Please enter a book name', 'error')
        return redirect(url_for('recommend_ui'))
    
    try:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), 
                              key=lambda x: x[1], reverse=True)[1:5]
        
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            data.append(item)
            
        current_year = datetime.now().year
        return render_template('recommend.html', data=data, search_query=user_input, current_year=current_year)
    
    except IndexError:
        flash('Book not found in our database. Please try another title.', 'error')
        return redirect(url_for('recommend_ui'))
    except Exception as e:
        app.logger.error(f"Error in recommendation: {str(e)}")
        flash('An error occurred while processing your request', 'error')
        return redirect(url_for('recommend_ui'))

if __name__ == '__main__':
    app.run(debug=True)