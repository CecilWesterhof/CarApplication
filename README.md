# CarApplication
A car application with Python and SQLite

A simple application to help you administer your car.

At the moment it is not very useful, but I will keep adding functionalities.

If you would like a particular function added: let me know.

To fill the tables with values the file tableValues.json needs to be filled like:
```json
    {
        "fuel": [
            [ date, odometer,  distance, liters, unit_price, payed_price, full_tank ],
            .
            .
            .
        ],
        "rides": [
            [ date, odometer, description ],
            .
            .
            .
        ]
    }
```

In full_tank a 1 represents True, other values False.
