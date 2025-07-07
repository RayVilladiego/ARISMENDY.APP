import streamlit as st
import pandas as pd
from utils.data_manager import (
    load_contenedores, save_contenedores,
    load_movimientos, save_movimientos
)

st.set_page_config(page_title="Arismendy App", layout="wide")
st.title("📦 ARISMENDY - Gestión de Contenedores")

menu = st.sidebar.selectbox(
    "Menú",
    ["Inventario", "Registrar Movimiento", "Nuevo Contenedor", "Historial"]
)

if menu == "Inventario":
    st.header("Inventario de Contenedores")
    try:
        contenedores = load_contenedores()
        st.dataframe(contenedores, use_container_width=True)
    except Exception as e:
        st.error(f"Error cargando datos: {e}")

elif menu == "Registrar Movimiento":
    st.header("Registrar Movimiento de Contenedor")
    try:
        contenedores = load_contenedores()
        movimientos = load_movimientos()

        if contenedores.empty:
            st.warning("⚠️ No hay contenedores registrados todavía.")
        else:
            cont_id = st.selectbox("Selecciona el contenedor", contenedores["ID"])
            origen = contenedores[contenedores["ID"] == cont_id]["UbicacionActual"].values[0]
            destino = st.selectbox(
                "Nueva ubicación",
                ["Patio 1", "Patio 2", "Patio 3", "Finca", "Oficina"]
            )
            responsable = st.text_input("Responsable del movimiento")
            observacion = st.text_area("Observaciones")

            if st.button("Guardar Movimiento"):
                # Actualizar ubicación
                contenedores.loc[contenedores["ID"] == cont_id, "UbicacionActual"] = destino
                save_contenedores(contenedores)

                # Registrar movimiento
                new_movimiento = pd.DataFrame([{
                    "MovimientoID": len(movimientos) + 1,
                    "ContenedorID": cont_id,
                    "FechaMovimiento": pd.Timestamp.now(),
                    "Origen": origen,
                    "Destino": destino,
                    "Responsable": responsable,
                    "Observacion": observacion
                }])

                movimientos = pd.concat([movimientos, new_movimiento], ignore_index=True)
                save_movimientos(movimientos)

                st.success("✅ Movimiento registrado exitosamente.")
    except Exception as e:
        st.error(f"Error: {e}")

elif menu == "Nuevo Contenedor":
    st.header("Registrar Nuevo Contenedor")
    try:
        with st.form("form_nuevo_contenedor"):
            id_ = st.text_input("ID único del contenedor")
            nombre = st.text_input("Nombre / Descripción")
            tipo = st.selectbox("Tipo", ["Oficina", "Bodega", "Sanitario", "Mixto", "Otro"])
            estado = st.selectbox("Estado", ["Disponible", "En uso", "En reparación"])
            ubicacion = st.selectbox(
                "Ubicación inicial",
                ["Patio 1", "Patio 2", "Patio 3", "Finca", "Oficina"]
            )
            largo = st.number_input("Largo (pies/ft)", min_value=0.0, step=1.0)
            material = st.text_input("Material base (Acero Corten, etc.)")
            nacionalizado = st.selectbox("Nacionalizado", ["Sí", "No"])
            fecha_nac = st.date_input("Fecha de nacionalización (opcional)")
            doc_nac = st.text_input("Link documento nacionalización (PDF en Drive)")
            img_ext = st.text_input("Link imagen exterior (Drive/URL)")
            img_int = st.text_input("Link imagen interior (Drive/URL)")
            obs = st.text_area("Observaciones técnicas, acabados, etc.")

            submit = st.form_submit_button("Guardar Contenedor")

            if submit:
                contenedores = load_contenedores()
                nuevo = pd.DataFrame([{
                    "ID": id_,
                    "Nombre": nombre,
                    "Tipo": tipo,
                    "Estado": estado,
                    "UbicacionActual": ubicacion,
                    "Largo": largo,
                    "MaterialBase": material,
                    "Nacionalizado": nacionalizado,
                    "FechaNacionalizacion": fecha_nac,
                    "DocumentoNacionalizacion": doc_nac,
                    "ImagenExterior": img_ext,
                    "ImagenInterior": img_int,
                    "Observaciones": obs
                }])
                contenedores = pd.concat([contenedores, nuevo], ignore_index=True)
                save_contenedores(contenedores)
                st.success(f"✅ Contenedor {id_} creado exitosamente.")
    except Exception as e:
        st.error(f"Error: {e}")

elif menu == "Historial":
    st.header("Historial de Movimientos")
    try:
        movimientos = load_movimientos()
        st.dataframe(movimientos, use_container_width=True)
    except Exception as e:
        st.error(f"Error cargando historial: {e}")
