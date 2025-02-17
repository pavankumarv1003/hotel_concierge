document.addEventListener('DOMContentLoaded', function() {
    const roomNumberInput = document.getElementById('roomNumber');
    const otpInput = document.getElementById('otp');
    const verifyBtn = document.getElementById('verifyBtn');
    const otpMessage = document.getElementById('otpMessage');
    const mainSection = document.getElementById('main-section');
    const orderRoomServiceBtn = document.getElementById('orderRoomServiceBtn'); //For now we will remove this
    const getMenuBtn = document.getElementById('getMenuBtn');
    const message = document.getElementById('message');

    verifyBtn.addEventListener('click', function() {
        const roomNumber = roomNumberInput.value;
        const otp = otpInput.value;

        if (!roomNumber || !otp) {
            otpMessage.textContent = 'Please enter both room number and OTP.';
            return;
        }

        fetch('http://localhost:8080/api/otp/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ room_number: roomNumber, otp: otp }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                otpMessage.textContent = data.message;
                otpMessage.style.color = 'green';
                document.getElementById('otp-section').style.display = 'none';
                mainSection.style.display = 'block';
            } else {
                otpMessage.textContent = data.error || 'Verification failed.';
                otpMessage.style.color = 'red';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            otpMessage.textContent = 'An error occurred.';
            otpMessage.style.color = 'red';
        });
    });

   // Add event listeners to the order buttons
    document.querySelectorAll('.order-button').forEach(button => {
        button.addEventListener('click', function() {
            const foodItem = this.dataset.item;
            sendOrderToDialogflow(foodItem);
        });
    });


    getMenuBtn.addEventListener('click', getMenu);
    function getMenu() {
        fetch('http://localhost:8080/menu') // No need for full URL, use relative path
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            message.textContent = "Menu: " + data.join(', '); // Display menu items
            message.style.color = 'black';
        })
        .catch(error => {
            console.error('Error fetching menu:', error);
            message.textContent = 'Error fetching menu.';
             message.style.color = 'red';
        });
    }
});

function sendOrderToDialogflow(foodItem) {
    const roomNumber = roomNumberInput.value; // Get the room number
    fetch('http://localhost:8080/', { // Send to your webhook
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ // Construct the Dialogflow request JSON
            queryResult: {
                queryText: "Order " + foodItem, // Construct a query
                intent: { displayName: "RoomService.OrderFood" }, // Specify the intent
                parameters: { food_item: foodItem, room_number: roomNumber }, // Include the food item and room number
            },
            session: "projects/your-project-id/agent/sessions/web-ui-session", // Replace with your project ID
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Display the response from Dialogflow (your Flask webhook)
        message.textContent = data.fulfillmentText;
          message.style.color = 'green';
    })
    .catch(error => {
        console.error('Error:', error);
        message.textContent = 'An error occurred while ordering.';
          message.style.color = 'red';
    });
}