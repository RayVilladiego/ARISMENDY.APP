import streamlit as st
import pandas as pd
from utils.data_manager import (
    load_contenedores,
    save_contenedores,
    load_movimientos,
    save_movimientos
)

st.set_page_config(page_title="Arismendy App", layout="wide")
st.title("📦 ARISMENDY - Gestión de Contenedores")

# 🔄 Carga datos
try:
    contenedores = load_contenedores()
    movimientos = load_movimientos()
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    contenedores = pd.DataFrame()
    movimientos = pd.DataFrame()

# 📌 Sidebar navegación
menu = st.sidebar.radio(
    "📊 Menú",
    ["Vista General", "Ventas", "Alquiler", "Movimientos", "Registrar Movimiento", "Nuevo Contenedor"]
)

# ✅ 1️⃣ Vista General
if menu == "Vista General":
    st.header("📊 Vista General del Inventario")

    if contenedores.empty:
        st.warning("⚠️ No hay datos de contenedores registrados.")
    else:
        total = len(contenedores)
        disponibles = contenedores[contenedores["Estado"] == "Disponible"]
        en_uso = contenedores[contenedores["Estado"] == "En uso"]
        en_reparacion = contenedores[contenedores["Estado"] == "En reparación"]
        nacionalizados = contenedores[contenedores["Nacionalizado"] == "Sí"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Contenedores", total)
        col2.metric("Disponibles", len(disponibles))
        col3.metric("En Uso", len(en_uso))
        col4.metric("En Reparación", len(en_reparacion))

        st.subheader("✅ Índice de Nacionalización")
        if total > 0:
            porcentaje_nac = (len(nacionalizados) / total) * 100
            st.progress(int(porcentaje_nac))
            st.write(f"**{porcentaje_nac:.1f}% nacionalizados**")
        else:
            st.write("No hay datos para calcular.")

        st.subheader("📦 Inventario por Tipo")
        tipo_count = contenedores['Tipo'].value_counts()
        st.bar_chart(tipo_count)

        st.subheader("📍 Distribución por Ubicación")
        ubicacion_count = contenedores['UbicacionActual'].value_counts()
        st.bar_chart(ubicacion_count)

# ✅ 2️⃣ Ventas
elif menu == "Ventas":
    st.header("💰 Dashboard de Ventas")

    if contenedores.empty:
        st.warning("⚠️ No hay contenedores cargados.")
    else:
        stock_vendible = contenedores[
            (contenedores["Estado"] == "Disponible") &
            (contenedores["Nacionalizado"] == "Sí")
        ]

        total = len(contenedores)
        nacionalizados = contenedores[contenedores["Nacionalizado"] == "Sí"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Stock Disponible para Venta", len(stock_vendible))
        if total > 0:
            col2.metric("Índice de Nacionalización", f"{(len(nacionalizados)/total)*100:.1f}%")
        else:
            col2.metric("Índice de Nacionalización", "0%")
        ingresos_estimados = len(stock_vendible) * 8000  # Simulación $8,000 por unidad
        col3.metric("Ingresos Potenciales", f"${ingresos_estimados:,.0f} USD")

        st.subheader("📦 Detalle de Stock Vendible")
        st.dataframe(stock_vendible, use_container_width=True)

# ✅ 3️⃣ Alquiler
elif menu == "Alquiler":
    st.header("🏢 Dashboard de Alquiler")

    if contenedores.empty:
        st.warning("⚠️ No hay contenedores cargados.")
    else:
        alquilados = contenedores[contenedores["Estado"] == "En uso"]
        total_disponible = len(contenedores)
        tasa_ocupacion = (len(alquilados) / total_disponible) * 100 if total_disponible > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Tasa de Ocupación", f"{tasa_ocupacion:.1f}%")
        col2.metric("Contenedores Alquilados", len(alquilados))
        ingreso_mensual = len(alquilados) * 500  # Simulado $500 por unidad
        col3.metric("Ingreso mensual estimado", f"${ingreso_mensual:,.0f} USD")

        st.subheader("📋 Lista de Contenedores Alquilados")
        st.dataframe(alquilados, use_container_width=True)

# ✅ 4️⃣ Movimientos
elif menu == "Movimientos":
    st.header("📈 Historial de Movimientos")

    if movimientos.empty:
        st.warning("⚠️ No hay movimientos registrados.")
    else:
        st.dataframe(movimientos, use_container_width=True)

        st.subheader("📊 Movimientos por Mes")
        movimientos['FechaMovimiento'] = pd.to_datetime(movimientos['FechaMovimiento'])
        movimientos['Mes'] = movimientos['FechaMovimiento'].dt.to_period('M')
        resumen = movimientos.groupby('Mes').size().reset_index(name='Movimientos')
        resumen['Mes'] = resumen['Mes'].astype(str)
        st.bar_chart(data=resumen, x='Mes', y='Movimientos')

        st.subheader("📍 Distribución por Ubicación Actual")
        ubicacion_count = contenedores['UbicacionActual'].value_counts()
        st.bar_chart(ubicacion_count)

# ✅ 5️⃣ Registrar Movimiento
elif menu == "Registrar Movimiento":
    st.header("🚚 Registrar Movimiento de Contenedor")
    if contenedores.empty:
        st.warning("⚠️ No hay contenedores registrados.")
    else:
        cont_id = st.selectbox("Selecciona contenedor", contenedores["ID"])
        origen = contenedores[contenedores["ID"] == cont_id]["UbicacionActual"].values[0]
        destino = st.selectbox(
            "Nueva ubicación",
            ["Patio 1", "Patio 2", "Patio 3", "Finca", "Oficina"]
        )
        responsable = st.text_input("Responsable del movimiento")
        observacion = st.text_area("Observaciones")

        if st.button("Guardar Movimiento"):
            contenedores.loc[contenedores["ID"] == cont_id, "UbicacionActual"] = destino
            save_contenedores(contenedores)

            new_mov = pd.DataFrame([{
                "MovimientoID": len(movimientos) + 1,
                "ContenedorID": cont_id,
                "FechaMovimiento": pd.Timestamp.now(),
                "Origen": origen,
                "Destino": destino,
                "Responsable": responsable,
                "Observacion": observacion
            }])
            movimientos = pd.concat([movimientos, new_mov], ignore_index=True)
            save_movimientos(movimientos)

            st.success("✅ Movimiento registrado exitosamente.")

# ✅ 6️⃣ Nuevo Contenedor
elif menu == "Nuevo Contenedor":
    st.header("➕ Registrar Nuevo Contenedor")
    with st.form("form_nuevo_contenedor"):
        id_ = st.text_input("ID único")
        nombre = st.text_input("Nombre / Descripción")
        tipo = st.selectbox("Tipo", ["Oficina", "Bodega", "Sanitario", "Mixto", "Otro"])
        estado = st.selectbox("Estado", ["Disponible", "En uso", "En reparación"])
        ubicacion = st.selectbox(
            "Ubicación inicial",
            ["Patio 1", "Patio 2", "Patio 3", "Finca", "Oficina"]
        )
        largo = st.number_input("Largo (pies/ft)", min_value=0.0, step=1.0)
        material = st.text_input("Material base")
        nacionalizado = st.selectbox("Nacionalizado", ["Sí", "No"])
        fecha_nac = st.date_input("Fecha de nacionalización (opcional)")
        doc_nac = st.text_input("Link documento nacionalización (PDF/Drive)")
        img_ext = st.text_input("Link imagen exterior (Drive/URL)")
        img_int = st.text_input("Link imagen interior (Drive/URL)")
        obs = st.text_area("Observaciones técnicas, acabados, etc.")

        submit = st.form_submit_button("Guardar Contenedor")

        if submit:
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
