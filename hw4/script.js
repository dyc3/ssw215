function newFood(name, price, variety) {
	return {
		name,
		price,
		variety,
	}
}

const USDtoPOUND = 0.71;

const FOODS = {
	breakfast: [
		newFood("Rainbow Muffin", 3, "High"),
		newFood("Pink Slime", 1, "Low"),
	],
	lunch: [
		newFood("Epic Clown Sandwich", 6, "High"),
		newFood("Humor Hoagie", 4, "Medium"),
		newFood("Pink Slime", 1, "Low"),
	],
	dinner: [
		newFood("Red Ribeye", 30, "Low"),
		newFood("Burger", 10, "High"),
		newFood("Pink Slime", 1, "Low"),
	]
}

const USD = 0;
const POUND = 1;

const CURRENCY_SYMBOLS = {
	[USD]: "$",
	[POUND]: "£",
}

let currencyMode = USD;

function toggleCurrency() {
	currencyMode = (currencyMode + 1) % 2;
	render();
}

function placeOrder() {
	let el = document.getElementById("orderconfirm");
	el.innerText = "We’ve received your order. Your order will be ready for pick up in 5 minutes.";
}

function render() {
	for (let category of ["breakfast", "lunch", "dinner"]) {
		let container = document.getElementById(category);
		container.innerHTML = "";

		for (const item of FOODS[category]) {
			let row = document.createElement("tr");

			let col = document.createElement("td");
			col.innerText = item.name;
			row.appendChild(col);

			col = document.createElement("td");
			col.innerText = `${CURRENCY_SYMBOLS[currencyMode]}${Math.round((currencyMode === USD ? item.price : item.price * USDtoPOUND) * 100) / 100}`;
			row.appendChild(col);

			col = document.createElement("td");
			col.innerText = item.variety;
			row.appendChild(col);

			container.appendChild(row);
		}
	}
}

render()
