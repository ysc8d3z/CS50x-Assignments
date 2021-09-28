// Do the following when the DOM content is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Will only prompt user for name if it is a new session
    if (sessionStorage.getItem('hasCodeRunBefore') === null) {
        let askUsersname = prompt('Hello there, what is your name? ');
        // Greet user with the name they entered
        if (askUsersname != null) {
            let usernameResponse = document.getElementById('name').innerHTML;
            usernameResponse = "Hello " + askUsersname + ", my name is Yusuf Siddiqui and this is my homepage for CS50x. Please take a look around!";
            // If user clicks cancel on the alert box show website regardless
            setTimeout(function() {
            if (confirm(usernameResponse) != true) {
                window.alert('It seems you have clicked "cancel", here is my homepage anyway.');
            }
            }, 0500);
        }
        // Greet stranger <-- if user clicks cancel on the greeting box
        else {
            let usernameResponse = document.getElementById('name').innerHTML;
            usernameResponse = "Hello stranger, my name is Yusuf Siddiqui and this is my homepage for CS50x. Please take a look around!";
            // If user clicks cancel on the alert box show website regardless
            setTimeout(function() {
            if (confirm(usernameResponse) != true) {
                window.alert('It seems you have clicked "cancel", here is my homepage anyway.');
            }
            }, 0500);
        }

        sessionStorage.setItem('hasCodeRunBefore', true);
    }
});