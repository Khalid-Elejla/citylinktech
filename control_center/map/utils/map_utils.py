import folium

def create_map(df, coordinates):
    m = folium.Map(tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png', attr='OpenStreetMap HOT')
    m.fit_bounds(coordinates)

    asterisk_columns = [col for col in df.columns if col.endswith('*')]
    tooltip_col = asterisk_columns[0] if asterisk_columns else None
    asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

    for idx, row in df.iterrows():
        popup_content = "".join(f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns)
        icon_color = 'blue' if row.get('Status*', '') == 'Closed' else 'red'
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<div><b>{row[tooltip_col]}</b><br>{popup_content}</div>",
            tooltip=row[tooltip_col] if tooltip_col else '',
            icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
        ).add_to(m)
    return m
