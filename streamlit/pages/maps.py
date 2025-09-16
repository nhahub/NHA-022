import streamlit as st
from streamlit_keplergl import keplergl_static
import arabic_reshaper
from bidi.algorithm import get_display
import pandas as pd
import pydeck as pdk
from app import data

from keplergl import KeplerGl


# Create a KeplerGl map instance
map_1 = KeplerGl(height=600)

# Add your data as a layer named "my_data"
map_1.add_data(data=data)

# Render map inside Streamlit
kepler_map = keplergl_static(map_1)
#---------------------------------------------------------------------------------------------
#extract coordinates 
def extract_coordinates(gdf):
    """Extract coordinates based on geometry type"""
    if gdf.geometry.geom_type.isin(["Point"]).any():
        gdf["lon"] = gdf.geometry.x
        gdf["lat"] = gdf.geometry.y
    else:
        # For LineString or Polygon, use centroid but handle CRS properly
        if gdf.crs and gdf.crs.is_geographic:
            # Project to a local CRS for better centroid calculation
            gdf_projected = gdf.to_crs('EPSG:3857')  # Web Mercator
            centroids = gdf_projected.geometry.centroid
            centroids_geo = centroids.to_crs(gdf.crs)
            gdf["lon"] = centroids_geo.x
            gdf["lat"] = centroids_geo.y
        else:
            gdf["lon"] = gdf.geometry.centroid.x
            gdf["lat"] = gdf.geometry.centroid.y
    return gdf

gdf = extract_coordinates(data)
print(gdf.columns)

def fix_arabic_text(text):
    """Properly format Arabic text for display"""
    if pd.isna(text) or text is None or str(text).strip() == '' or str(text) == 'None':
        return "Unknown Street"
    
    text_str = str(text).strip()
    
    
    if any('\u0600' <= char <= '\u06FF' for char in text_str):
        return text_str
    
    
    try:
        
        if 'Ø' in text_str or 'Ù' in text_str or 'Ù‚' in text_str:
            
            try:
                
                fixed_text = text_str.encode('latin1').decode('utf-8')
                # Now reshape and reorder for proper display
                reshaped = arabic_reshaper.reshape(fixed_text)
                return get_display(reshaped)
            except:
                pass
        
        
        if any('\u0600' <= char <= '\u06FF' for char in text_str):
            reshaped = arabic_reshaper.reshape(text_str)
            return get_display(reshaped)
    except:
        pass
    
    return text_str
gdf["name_fixed"] = gdf.get('name', 'Unknown Street').apply(fix_arabic_text)

def get_damage_severity(confidence):
    """Categorize damage severity based on confidence"""
    if confidence >= 0.8:
        return "High"
    elif confidence >= 0.6:
        return "Medium"
    elif confidence >= 0.4:
        return "Low"
    else:
        return "Uncertain"
    

def get_severity_color(severity):
    """Get color based on damage severity"""
    colors = {
        "High": [220, 20, 60, 220],        # Crimson Red
        "Medium": [255, 140, 0, 200],       # Dark Orange  
        "Low": [255, 215, 0, 180],          # Gold
        "Uncertain": [105, 105, 105, 160]   # Dim Gray
    }
    return colors.get(severity, [105, 105, 105, 160])

gdf['severity'] = gdf['confidence'].apply(get_damage_severity)
gdf['damage_type'] = gdf['label'].fillna('unknown')
gdf['confidence_pct'] = (gdf['confidence'] * 100).round(1)
gdf['color'] = gdf['severity'].apply(get_severity_color)


heatmap_layer = pdk.Layer(
    "HeatmapLayer",
    data=gdf,
    get_position=["lon", "lat"],
    get_weight='confidence',  # Weight by confidence
    aggregation="MEAN",
    radiusPixels=60,  # Smaller heatmap radius
    intensity=1.2,    # Lower intensity
    colorRange=[
        [46, 204, 113, 80],        # Emerald Green (low density) - more transparent
        [241, 196, 15, 120],       # Sunflower Yellow
        [230, 126, 34, 160],       # Carrot Orange  
        [231, 76, 60, 200],        # Alizarin Red (high density)
    ],
    pickable=False,
)


scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=gdf,
    get_position=["lon", "lat"],
    get_fill_color='color',
    get_radius='confidence * 15 + 8',  # Much smaller size: 8-23 pixels
    pickable=True,
    stroked=True,
    get_line_color=[255, 255, 255, 255],
    get_line_width=1,  # Thinner border
)


tooltip = {
    "html": """
    <div style="font-family: 'Segoe UI', Tahoma, Arial, sans-serif; max-width: 320px; line-height: 1.4;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px; margin: -10px -10px 10px -10px; border-radius: 8px 8px 0 0;">
            <h3 style="margin: 0; font-size: 16px; font-weight: 600;">🛣️ Pavement Damage Report</h3>
        </div>
        
        <div style="padding: 2px 0;">
            <div style="margin-bottom: 8px;">
                <span style="color: #555; font-size: 12px; font-weight: 500;">📍 Street:</span><br>
                <div style="font-size: 14px; font-weight: 600; color: #2c3e50; direction: rtl; text-align: right; font-family: 'Arial', 'Tahoma', sans-serif;">{name_fixed}</div>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <div style="flex: 1; margin-right: 10px;">
                    <span style="color: #555; font-size: 12px; font-weight: 500;">⚠️ Damage Type:</span><br>
                    <span style="font-size: 13px; font-weight: 600; color: #e74c3c; text-transform: capitalize;">{damage_type}</span>
                </div>
                <div style="flex: 1;">
                    <span style="color: #555; font-size: 12px; font-weight: 500;">📊 Severity:</span><br>
                    <span style="font-size: 13px; font-weight: bold; color: {severity_color};">{severity}</span>
                </div>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 8px; border-radius: 6px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #555; font-size: 12px;">🎯 Confidence:</span>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 80px; height: 6px; background-color: #e0e0e0; border-radius: 3px; margin-right: 8px;">
                            <div style="width: {confidence}%; height: 100%; background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1); border-radius: 3px;"></div>
                        </div>
                        <span style="font-weight: bold; color: #2c3e50; font-size: 13px;">{confidence_pct}%</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """,
    "style": {
        "backgroundColor": "white",
        "color": "#333",
        "border": "1px solid #ddd",
        "borderRadius": "10px",
        "padding": "10px",
        "fontSize": "12px",
        "boxShadow": "0 8px 25px rgba(0,0,0,0.15)",
        "maxWidth": "320px"
    }
}


severity_colors = {
    "High": "#DC143C",      # Crimson
    "Medium": "#FF8C00",    # Dark Orange
    "Low": "#83C763",       # Gold  
    "Uncertain": "#1BDA14"  # Dim Gray
}
gdf['severity_color'] = gdf['severity'].map(severity_colors)

view_state = pdk.ViewState(
    latitude=gdf["lat"].mean(),
    longitude=gdf["lon"].mean(),
    zoom=12,
    pitch=45,
    bearing=0,
)

r = pdk.Deck(
    layers=[heatmap_layer, scatter_layer],
    initial_view_state=view_state,
    tooltip=tooltip,
    map_style='https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
)


r = pdk.Deck(
    layers=[heatmap_layer, scatter_layer],
    initial_view_state=view_state,
    tooltip=tooltip,
    map_style='https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',  # Free Carto basemap, no token required
)

# r.to_html('heatmap.html', notebook_display=False)

st.pydeck_chart(r)