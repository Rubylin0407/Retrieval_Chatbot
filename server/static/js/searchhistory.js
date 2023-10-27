// Call the fetchQAHistory function when the page loads
document.addEventListener('DOMContentLoaded', function () {
    fetchQAHistory();
});

// Function to fetch QA-history data from MongoDB and display question-answer pairs in a table
async function fetchQAHistory() {
    try {
        const response = await fetch('/api/v1/get-qa-history');
        const user_data = await response.json();

        // Get a reference to the table element in your HTML
        const table = document.getElementById('QA-history-table');

        // Fetch the user's favorite items
        const favorites = await fetchUserFavorites(); // Implement this function

        // Loop through the user_data and create table rows for each question-answer pair
        user_data.forEach(entry => {
            const question = entry.question;
            const rawAnswer = entry.answer;

            // Parse rawAnswer to transform URLs into clickable links
            const linkedAnswer = rawAnswer.replace(
                /\[([^\]]+)\]\((https?:\/\/[^\s\)]+)\)/g,
                '<a href="$2" target="_blank">$1</a>'
            );

            const QA_pair_id = entry.id_str;

            // Create a new table row
            const row = table.insertRow();

            // Create table cells for question and answers
            const questionCell = row.insertCell(0);
            const answerCell = row.insertCell(1);

            // Populate the table cells with question and answers
            questionCell.innerText = `${question}`;
            answerCell.innerHTML = linkedAnswer; // Use innerHTML here because we're inserting HTML content

            // Create a button cell and button element
            const buttonCell = row.insertCell(2);
            const addButton = document.createElement('button');

            // Check if the current item is in the user's favorites
            if (favorites.includes(QA_pair_id)) {
                addButton.classList.add('favorite');
                addButton.innerHTML = '&#10084;'; // Solid heart
            } else {
                addButton.innerHTML = '&#9825'; // Outline heart
            }

            addButton.addEventListener('click', () => {
                // Handle the "Add to Favorites" action here
                addToFavorites(QA_pair_id, addButton);
            });
            buttonCell.appendChild(addButton);
        });
    } catch (error) {
        console.error('Error fetching QA-history data:', error);
    }
}


// Function to fetch the user's favorite items
async function fetchUserFavorites() {
    try {
        const response = await fetch('/api/v1/get-user-favorites');
        const favorites = await response.json();
        return favorites.map(fav => fav.QA_pair_id);
    } catch (error) {
        console.error('Error fetching user favorites:', error);
        return [];
    }
}

// Function to handle the "Add to Favorites" action
function addToFavorites(QA_pair_id, button) {
    // Check if the button already has a class "favorite"
    if (button.classList.contains('favorite')) {
        // If it does, remove the class and change the heart to outline
        button.classList.remove('favorite');
        button.innerHTML = '&#9825'; // Change to outline heart
        // Implement your logic to remove the item from favorites here
        removeFavorite(QA_pair_id);
    } else {
        // If it doesn't have the class, add the class and change the heart to solid
        button.classList.add('favorite');
        button.innerHTML = '&#10084;'; // Change to solid heart
        // Implement your logic to add the item to favorites here
        addFavorite(QA_pair_id);
    }
}

// Function to add an item to the user's favorites
async function addFavorite(QA_pair_id) {
    try {
        await fetch('/api/v1/add-favorite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({QA_pair_id })
        });
        console.log('Added to Favorites:', QA_pair_id);
    } catch (error) {
        console.error('Error adding to Favorites:', error);
    }
}

// Function to remove an item from the user's favorites
async function removeFavorite(QA_pair_id) {
    try {
        await fetch('/api/v1/remove-favorite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ QA_pair_id })
        });
        console.log('Removed from Favorites:', QA_pair_id);
    } catch (error) {
        console.error('Error removing from Favorites:', error);
    }
}