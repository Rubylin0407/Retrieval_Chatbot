async function submitForm(event) {
    event.preventDefault();

    const formData = new FormData(document.getElementById('signup-form'));

    try {
        const response = await fetch('/user/signup', {
            method: 'POST',
            body: formData
        });

        if (response.status === 400) {
            const errorText = await response.text();
            alert(errorText);
        } else if (response.status === 403) {
            alert('Email already exists.');
        } else if (response.ok) {
            location.href = "/user/login";
        } else {
            alert('An error occurred. Please try again.');
        }
    } catch (error) {
        console.error('There was an error submitting the form:', error);
        alert('An error occurred. Please try again.');
    }
}