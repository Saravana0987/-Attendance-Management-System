

function validateForm() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("user-email").value;
    const phoneNumber = document.getElementById("phoneNumber").value;
    const gender = document.querySelector('input[name="gender"]:checked');
    const password = document.getElementById("user-password").value;
    const confirmPassword = document.getElementById("Confirmation-password").value;
    const nameError=document.getElementById("nameError");
    const emailError=document.getElementById("emailError");
    const phoneError=document.getElementById("phoneError");
    const genderError=document.getElementById("genderError");
    const passwordError=document.getElementById("passwordError");
    const confrimPasswordError=document.getElementById("confirmPasswordError");
    const batch = document.getElementById("batch").value;
    const branch = document.getElementById("branch").value;
    const batchError=document.getElementById("batchError");
    const branchError=document.getElementById("branchError");
    const sem= document.getElementById("Sem").value;
    const semError=document.getElementById("semError");
    const subjects = document.querySelectorAll('input[name="subjects[]"]:checked');
    const subjectsError=document.getElementById("subjectsError");
    const Idnumber= document.getElementById("Idnumber").value;
    const IdError=document.getElementById("IdError");
    var isValid = true;

    if (name === "") {
        nameError.textContent = "Please enter your name.";
        isValid = false;
    } else {
         nameError.textContent = "";
    }

    var emailRegex= /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        emailError.textContent = "Please enter a valid Email.";
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

    if (!gender) {
        genderError.textContent = "Please select a gender.";
        isValid = false;
    } else {
        genderError.textContent = "";
    }
var passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@#$|,._]{8,}/;
if (!passwordRegex.test(password)) {
    passwordError.textContent = "Password must contain at least one lowercase letter, one uppercase letter, and one digit.Length should be Eight.";
    isValid = false;
} else {
    passwordError.textContent = "";
}

if (confirmPassword === "") {
    confrimPasswordError.textContent = "Please confirm your password.";
    isValid = false;
} else if (password !== confirmPassword) {
    confirmPasswordError.textContent = "Passwords do not match.";
    isValid = false;
} else {
    confirmPasswordError.textContent = "";

}
if (sem === "choose") {
    semError.textContent = "Please select  semister";
    isValid = false;
 
} else {
    semError.textContent = ""; 
  }

if (batch === "choose") {
    batchError.textContent = "Please select batch";
    isValid = false;
 
} else {
    batchError.textContent = "";

  }
  if (branch === "choose") {
    branchError.textContent = "Please select branch";
    isValid = false;
 
} else {
    branchError.textContent = ""; 
  }

  if (subjects.length === 0) {
    subjectsError.textContent = "Please select at least one subject.";
    isValid=false;


}  

var IdNumberRegex = /^[r|R]+([0][1-9]{1}|[1][1-9]{1}|[2][0-4]{1})[0-9]{4}$/;
    if (!IdNumberRegex.test(Idnumber)) {
        IdError.textContent = "Please enter a valid Id number.";
        isValid = false;
    }
    else if (Idnumber === "") {
        IdError.textContent = "Please enter your Id Number.";
        isValid = false;
    } 
    
    else {
        IdError.textContent = "";
    }

    return isValid;
}
 