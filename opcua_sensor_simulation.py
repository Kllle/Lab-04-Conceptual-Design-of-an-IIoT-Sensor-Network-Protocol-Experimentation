import asyncio
import random
from asyncua import ua, Server

async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    objects = await server.nodes.objects
    myobj = await objects.add_object(idx, "MyObject")

    temperature = await myobj.add_variable(idx, "Temperature", 0.0)
    humidity = await myobj.add_variable(idx, "Humidity", 0.0)

    await temperature.set_writable()
    await humidity.set_writable()

    async with server:
        while True:
            temp_value = random.uniform(20.0, 25.0)
            hum_value = random.uniform(30.0, 50.0)

            await temperature.write_value(temp_value)
            await humidity.write_value(hum_value)

            print(f"Temperature: {temp_value}, Humidity: {hum_value}")
            await asyncio.sleep(1)

asyncio.run(main())
