# EMS + PFS

There are five components inside the EMS+PFS Spine ToolBox project:

- **Input mibel** is the input of the **Run EMS** component and contains information regarding the players and their price/amount bids for each period. The schema that validates this input is available at ./run-ems/resources/generalSchema.json.
- **Player buses** is one of the inputs of the **Run PFS** component. This file maps the players present in the MIBEL market to the buses of the network defined in the **Input pfs**.
- **Input pfs** is one of the inputs of the **Run PFS** component and contains information regarding the elements of the network, as well as the powerflow algorithm to be used and its parameters. The schema that validates this input is available at ./run-pfs/resources/pfs_schema.json.
- **Run EMS** executes the MIBEL day-ahead market (defined in the input of the previous component), validating it with the JSON schema available at <https://em.gecad.isep.ipp.pt/api/v1/mibel/schema>. The results of simulating the MIBEL market are then sent to the **Run PFS** tool.
- **Run PFS** executes the Power Flow service receiving the network, the powerflow algorithm to be used and the loads of each bus by mapping the players' results to the buses. It also validates the **Input pfs** with the JSON schema available at <https://pf.gecad.isep.ipp.pt/api/v1/networks/schemas/generalSchema>. The results are then saved in a JSON file.