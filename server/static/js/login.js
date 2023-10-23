async function submitForm(event) {
    event.preventDefault();

    const formData = new FormData(document.getElementById('login-form'));

    try {
        const response = await fetch('/user/login', {
            method: 'POST',
            body: formData
        });

        if (response.status === 403) {
            const errorText = await response.text();
            alert(errorText);
        } else if (response.ok) {
            location.href = "/";
        } else {
            alert('An error occurred. Please try again.');
        }
    } catch (error) {
        console.error('There was an error submitting the form:', error);
        alert('An error occurred. Please try again.');
    }
}