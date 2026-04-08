import pandas as pd
import networkx as nx
import pickle
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# -----------------------------------
# STEP 1: Load dataset
# -----------------------------------
df = pd.read_csv("data/budget_data.csv")

print("\nOriginal Data:")
print(df.head())

# -----------------------------------
# STEP 2: Clean column names
# -----------------------------------
df.columns = df.columns.str.strip().str.lower()

# -----------------------------------
# STEP 3: Clean category values
# -----------------------------------
df["category"] = df["category"].astype(str).str.strip().str.lower()

df["category"] = df["category"].replace({
    "restuarant": "restaurant",
    "coffe": "coffee"
})

# -----------------------------------
# STEP 4: Convert date column
# -----------------------------------
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# -----------------------------------
# STEP 5: Drop missing values
# -----------------------------------
df = df.dropna(subset=["date", "category", "amount"])

# -----------------------------------
# STEP 6: Sort by date
# -----------------------------------
df = df.sort_values(by="date").reset_index(drop=True)

print("\nCleaned Data:")
print(df.head())

# -----------------------------------
# STEP 7: Create transitions
# -----------------------------------
edges = []

for i in range(len(df) - 1):
    source = df.loc[i, "category"]
    target = df.loc[i + 1, "category"]

    if source != target:
        edges.append((source, target))

print("\nSample Transitions:")
print(edges[:10])

# -----------------------------------
# STEP 8: Build directed weighted graph
# -----------------------------------
G = nx.DiGraph()

for source, target in edges:
    if G.has_edge(source, target):
        G[source][target]["weight"] += 1
    else:
        G.add_edge(source, target, weight=1)

print("\nGraph Summary:")
print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())

# -----------------------------------
# STEP 9: Save cleaned dataset
# -----------------------------------
df.to_csv("data/cleaned_budget_data.csv", index=False)

# -----------------------------------
# STEP 10: Save edge list
# -----------------------------------
edge_data = []
for u, v, d in G.edges(data=True):
    edge_data.append([u, v, d["weight"]])

edge_df = pd.DataFrame(edge_data, columns=["source", "target", "weight"])
edge_df.to_csv("data/edge_list.csv", index=False)

# -----------------------------------
# STEP 11: Save graph
# -----------------------------------
with open("data/graph.gpickle", "wb") as f:
    pickle.dump(G, f)

print("\nFiles saved successfully:")
print("- data/cleaned_budget_data.csv")
print("- data/edge_list.csv")
print("- data/graph.gpickle")

# -----------------------------------
# STEP 12: Final Non-Overlapping Graph
# -----------------------------------
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

top_edges = sorted(G.edges(data=True), key=lambda x: x[2]["weight"], reverse=True)[:10]

H = nx.DiGraph()
for u, v, d in top_edges:
    H.add_edge(u, v, weight=d["weight"])

# fixed node sizes
node_sizes_map = {
    "market": 7800,
    "coffee": 6800,
    "restaurant": 5200,
    "business lunch": 4300,
    "transport": 2200
}
node_sizes = [node_sizes_map.get(node, 2500) for node in H.nodes()]

# fixed colors
node_color_map = {
    "coffee": "#58C4C0",
    "market": "#FF6B6B",
    "restaurant": "#F4C95D",
    "business lunch": "#6A4C93",
    "transport": "#1A936F"
}
node_colors = [node_color_map.get(node, "#90BE6D") for node in H.nodes()]

# manual positions
pos = {
    "business lunch": (-2.8, 1.4),
    "market": (0.2, 0.6),
    "coffee": (-0.9, -0.5),
    "restaurant": (-1.4, -2.0),
    "transport": (3.2, 0.0)
}

plt.figure(figsize=(14, 9))

# draw nodes
nx.draw_networkx_nodes(
    H, pos,
    node_size=node_sizes,
    node_color=node_colors,
    edgecolors="black",
    linewidths=1.5
)

# draw labels
nx.draw_networkx_labels(
    H, pos,
    font_size=11,
    font_weight="bold"
)

# draw edges
for u, v, d in H.edges(data=True):
    if {u, v} == {"coffee", "market"}:
        rad = 0.32 if u == "coffee" else -0.32
    elif {u, v} == {"coffee", "restaurant"}:
        rad = 0.22 if u == "coffee" else -0.22
    elif {u, v} == {"business lunch", "market"}:
        rad = 0.12
    else:
        rad = 0.08

    nx.draw_networkx_edges(
        H, pos,
        edgelist=[(u, v)],
        edge_color="gray",
        arrows=True,
        arrowsize=22,
        width=2,
        connectionstyle=f"arc3,rad={rad}"
    )

# draw normal edge labels except coffee-market pair
normal_edge_labels = {}
for u, v, d in H.edges(data=True):
    if {u, v} != {"coffee", "market"}:
        normal_edge_labels[(u, v)] = d["weight"]

nx.draw_networkx_edge_labels(
    H, pos,
    edge_labels=normal_edge_labels,
    font_size=11,
    font_color="darkred",
    rotate=False,
    bbox=dict(facecolor="white", edgecolor="none", alpha=0.9)
)

# MANUALLY place coffee-market values
if H.has_edge("coffee", "market"):
    plt.text(
        -0.35, -0.05, str(H["coffee"]["market"]["weight"]),
        fontsize=11, color="darkred",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.9)
    )

if H.has_edge("market", "coffee"):
    plt.text(
        -0.55, 0.15, str(H["market"]["coffee"]["weight"]),
        fontsize=11, color="darkred",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.9)
    )

# legend
legend_elements = [
    Patch(facecolor="#58C4C0", edgecolor="black", label="Node = category"),
    Line2D([0], [0], color="gray", lw=2, label="Edge = transition"),
    Line2D([0], [0], marker=">", color="gray", linestyle="None", markersize=10, label="Arrow = direction"),
]

plt.legend(handles=legend_elements, loc="upper left", fontsize=11, frameon=True)

plt.title("Top Spending Category Transitions", fontsize=20, fontweight="bold", pad=20)
plt.xlabel("Edge labels show transition frequency.", fontsize=11, labelpad=15)

plt.axis("off")
plt.xlim(-4, 4)
plt.ylim(-2.8, 2.4)
plt.tight_layout()
plt.show()