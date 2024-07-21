document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const cardImage = document.getElementById('cardImage');
    const rejectButton = document.getElementById('rejectButton');
    const nextButton = document.getElementById('nextButton');
    const wishlistButton = document.getElementById('wishlistButton');
    const suggestedContainer = document.getElementById('suggestedContainer'); // Container for hardcoded suggestions
    let currentIndex = 0;
    let recommendations = [];
    let hardcodedSuggestions = []; // Hardcoded suggestions array

    uploadButton.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('http://localhost:5000/upload', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('File upload failed');
                }

                const data = await response.json();
                recommendations = data.recommendations;
                hardcodedSuggestions = data.suggested_images;

                currentIndex = 0;
                displayRecommendation();
                displayHardcodedSuggestions();
            } catch (error) {
                console.error('Error:', error);
            }
        }
    });

    function displayRecommendation() {
        if (recommendations.length > 0) {
            const rec = recommendations[currentIndex];
            cardImage.src = rec;
        }
    }

    function displayHardcodedSuggestions() {
        suggestedContainer.innerHTML = ''; // Clear previous suggestions
        hardcodedSuggestions.forEach(image => {
            const imgElement = document.createElement('img');
            imgElement.src = image; // Assuming image path is directly provided
            imgElement.classList.add('hardcoded-suggestion');
            suggestedContainer.appendChild(imgElement);
        });
    }

    rejectButton.addEventListener('click', () => {
        if (recommendations.length > 0) {
            currentIndex = (currentIndex + 1) % recommendations.length;
            displayRecommendation();
        }
    });

    nextButton.addEventListener('click', () => {
        if (recommendations.length > 0) {
            currentIndex = (currentIndex + 1) % recommendations.length;
            displayRecommendation();
        }
    });

    wishlistButton.addEventListener('click', async () => {
        if (recommendations.length > 0) {
            const rec = recommendations[currentIndex];
            try {
                const response = await fetch('http://localhost:5000/wishlist', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ image: rec })
                });

                if (!response.ok) {
                    throw new Error('Failed to save to wishlist');
                }

                // Toggle heart icon and wishlist status
                wishlistButton.classList.toggle('added');
                alert('Saved to wishlist!');
            } catch (error) {
                console.error('Error:', error);
            }
        }
    });
});
