const formValues = ["name", "email", "password"];
for (let i = 0; i < formValues.length; i++) {
    const value = formValues[i];
    if (!value) {
        console.log("false");
        break;
    }

    console.log("true");
}

for (const value of formValues) {
    if (value) {
        console.log("false");
        break;
    }

    console.log("true");
}