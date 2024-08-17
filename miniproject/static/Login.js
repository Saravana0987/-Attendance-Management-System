
function validateForm1() {
    const name = document.getElementById("name1").value;
    const email = document.getElementById("user-email1").value;
    const phoneNumber = document.getElementById("phoneNumber1").value;
    const password = document.getElementById("user-password1").value;
    const nameError=document.getElementById("nameError1");
    const emailError=document.getElementById("emailError1");
    const phoneError=document.getElementById("phoneError1");
    const passwordError=document.getElementById("passwordError1");
     var isValid = true;

    if (name === "") {
        nameError.textContent = "Please enter your name.";
        isValid = false;
    } else {
         nameError.textContent = "";
    }

    var emailRegex= /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        emailError.textContent = "Please enter a valid 10-digit phone number.";
        isValid = false;
    } else {
        emailError.textContent = "";
    }

    var phoneNumberRegex = /^[6-9]{1}[0-9]{9}$/;
    if (!phoneNumberRegex.test(phoneNumber)) {
       phoneError.textContent = "Please enter a valid 10-digit phone number.";
        isValid = false;
    } else {
         phoneError.textContent = "";
    }

    
var passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@#$|,._]{8,}$/;
if (!passwordRegex.test(password)) {
    passwordError.textContent = "Password must contain at least one lowercase letter, one uppercase letter, and one digit.Length should be eight letters.";
    isValid = false;
} else {
    passwordError.textContent = "";
}
 

    return isValid;


}
