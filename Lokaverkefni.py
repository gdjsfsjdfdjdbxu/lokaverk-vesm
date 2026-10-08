import asyncio
import json
from nicegui import ui
from aiomqtt import Client

MQTT_BROKER = "10.201.48.125"
MQTT_TOPIC = "gdjsfsjdfdjdbxu"

vekjarar = []

timi = ui.input("Vekjaraklukka", placeholder="Sláðu inn tíma")


async def senda():
    async with Client(MQTT_BROKER) as client:
        skilabod = json.dumps(vekjarar, ensure_ascii=False).encode()
        print("SENDI:", skilabod)
        await client.publish(MQTT_TOPIC, payload=skilabod)


def athuga_tima(e):
    gildi = e.args

    if len(gildi) != 4:
        return

    if not gildi.isdigit():
        return

    klst = int(gildi[:2])
    min = int(gildi[2:])

    if klst > 23 or min > 59:
        return

    timi.value = gildi


def velja_dag(timi, dagur):
    for vekjari in vekjarar:
        if vekjari["Tími"] == timi:

            if dagur in vekjari["Dagar"]:
                vekjari["Dagar"].remove(dagur)
            else:
                vekjari["Dagar"].append(dagur)

            break

    tafla.rows = vekjarar
    tafla.update()

    asyncio.create_task(senda())


def eyda_tima(vekjari):
    vekjarar.remove(vekjari)

    tafla.rows = vekjarar
    tafla.update()

    asyncio.create_task(senda())


def takki():
    gildi = timi.value

    if len(gildi) != 4:
        return

    if not gildi.isdigit():
        return

    klst = int(gildi[:2])
    min = int(gildi[2:])

    if klst > 23 or min > 59:
        return

    klukka = gildi[:2] + ":" + gildi[2:]

    if klukka in [x["Tími"] for x in vekjarar]:
        return

    vekjarar.append({
        "Tími": klukka,
        "Dagar": []
    })

    vekjarar.sort(key=lambda x: x["Tími"])

    tafla.rows = vekjarar
    tafla.update()

    timi.value = ""

    asyncio.create_task(senda())


timi.on("update:model-value", athuga_tima)

ui.button("Setja inn", on_click=takki)


tafla = ui.table(
    columns=[
        {
            "name": "Tími",
            "label": "Tími",
            "field": "Tími"
        },
        {
            "name": "Dagar",
            "label": "Vikudagar",
            "field": "Dagar"
        },
        {
            "name": "Eyða",
            "label": "Eyða",
            "field": "Eyða"
        }
    ],
    rows=vekjarar
)


tafla.add_slot(
    "body-cell-Dagar",
    """
    <q-td :props="props">
        <div style="display: flex; gap: 4px;">

            <q-btn
                label="MÁ"
                :color="props.row.Dagar.includes('Mánudagur') ? 'primary' : 'grey'"
                :outline="!props.row.Dagar.includes('Mánudagur')"
                @click="$parent.$emit('velja_dag', {
                    timi: props.row.Tími,
                    dagur: 'Mánudagur'
                })"
            />

            <q-btn
                label="Þ"
                :color="props.row.Dagar.includes('Þriðjudagur') ? 'primary' : 'grey'"
                :outline="!props.row.Dagar.includes('Þriðjudagur')"
                @click="$parent.$emit('velja_dag', {
                    timi: props.row.Tími,
                    dagur: 'Þriðjudagur'
                })"
            />

            <q-btn
                label="MI"
                :color="props.row.Dagar.includes('Miðvikudagur') ? 'primary' : 'grey'"
                :outline="!props.row.Dagar.includes('Miðvikudagur')"
                @click="$parent.$emit('velja_dag', {
                    timi: props.row.Tími,
                    dagur: 'Miðvikudagur'
                })"
            />

            <q-btn
                label="FI"
                :color="props.row.Dagar.includes('Fimmtudagur') ? 'primary' : 'grey'"
                :outline="!props.row.Dagar.includes('Fimmtudagur')"
                @click="$parent.$emit('velja_dag', {
                    timi: props.row.Tími,
                    dagur: 'Fimmtudagur'
                })"
            />

            <q-btn
                label="FÖ"
                :color="props.row.Dagar.includes('Föstudagur') ? 'primary' : 'grey'"
                :outline="!props.row.Dagar.includes('Föstudagur')"
                @click="$parent.$emit('velja_dag', {
                    timi: props.row.Tími,
                    dagur: 'Föstudagur'
                })"
            />

            <q-btn
                label="L"
                :color="props.row.Dagar.includes('Laugardagur') ? 'primary' : 'grey'"
                :outline="!props.row.Dagar.includes('Laugardagur')"
                @click="$parent.$emit('velja_dag', {
                    timi: props.row.Tími,
                    dagur: 'Laugardagur'
                })"
            />

            <q-btn
                label="S"
                :color="props.row.Dagar.includes('Sunnudagur') ? 'primary' : 'grey'"
                :outline="!props.row.Dagar.includes('Sunnudagur')"
                @click="$parent.$emit('velja_dag', {
                    timi: props.row.Tími,
                    dagur: 'Sunnudagur'
                })"
            />

        </div>
    </q-td>
    """
)


tafla.add_slot(
    "body-cell-Eyða",
    """
    <q-td :props="props">
        <q-btn
            label="Eyða"
            color="negative"
            @click="$parent.$emit('eyda', props.row)"
        />
    </q-td>
    """
)


tafla.on(
    "velja_dag",
    lambda e: velja_dag(
        e.args["timi"],
        e.args["dagur"]
    )
)


tafla.on(
    "eyda",
    lambda e: eyda_tima(e.args)
)


ui.run()
