// Validate input email, number, file, text
function validateInput(inputEl)
{
    if (inputEl.type == "email")
    {

        const valid = inputEl.value.match(/[a-z\d]+\@[a-z\d]+\.com/g);
        if (valid == null || inputEl.value == "")
        {
            return false;
        }
    }

    if (inputEl.type == "number")
    {
        if (isNaN(inputEl.value) || inputEl.value < 1)
        {
            return false;
        }
    }

    if (inputEl.type == "file")
    {
        if (inputEl == undefined)
        {
            return false;
        }
    }

    if (inputEl.value == "")
    {
        return false;
    }

    return true;
}

// Add a red border around input element for 2 second
function showInputError(inputEl)
{
    inputEl.classList.add('input-text-error');

    setTimeout(() => {
        inputEl.classList.remove('input-text-error');
        inputEl.focus();
    }, 2000);
}

// Make http requests with fetch
async function request(url, method, data=null)
{
    if (method.toUpperCase() === "POST")
    {
        // POST request
        const headers = {'Content-Type': 'application/json'}

        try
        {
            const req = await fetch(url, {
                method,
                headers: headers,
                body: JSON.stringify(data)
            });

            return req.json();
        }
        catch (error)
        {
            console.error('Error:', error);
        }
    }
    else
    {
        // GET request
        try
        {
            const req = await fetch(url);
            return req.json();
        }
        catch (error)
        {
            console.error('Error', error);
        }
    }
}

/*
Parse string Nodes to HTML element

https://developer.mozilla.org/en-US/docs/Web/API/Range/createContextualFragment
https://developer.mozilla.org/en-US/docs/Web/API/Document/createRange
*/
function parseDom(html)
{
    const range = document.createRange();
    const nodes = range.createContextualFragment(html);
    return nodes;
}

function getIsoDate(date)
{
    return `
        ${date.getFullYear()}-
        ${String(date.getMonth() + 1).padStart(2, "0")}-
        ${String(date.getDate()).padStart(2, "0")}T
        ${String(date.getHours()).padStart(2, "0")}:
        ${String(date.getMinutes()).padStart(2, "0")}
    `.split(" ").join("").split("\n").join("");
}

// https://stackoverflow.com/questions/563406/how-to-add-days-to-date
function addDays(date, days) {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}
