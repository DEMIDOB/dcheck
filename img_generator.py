import imgkit


def gen_img(idx, f_name, l_name, phone, total, data):
    prs = ""

    i = 0
    for pr in data:
        prs += f"""<div class="product flexrow">
                        <div class="productName">{i + 1}. {pr["title"]}</div>
                        <div class="productPrice">{pr["amount"]} x <span class="price">{pr["price"]}</span></div> 
                    </div>"""
        i += 1

#     contents = f"""
#     </head>
#     <body>
#         <div class="container">
#             <div class="head">
#                 <div class="row">
#                     <div class="col-md-6">
#                         <div class="number">№08</div>
#
#                         <div class="name">
#                             <span>{f_name} {l_name}</span>
#                         </div>
#                     </div>
#                     <div class="col-md-6">
#                         <div class="phone"><span>т. {phone}</span> </div>
#                     </div>
#                 </div>
#                     <hr />
#
#                 </div>
#                 <div class="products">
#                     {prs}
#                 </div>
#                 <div class="fullPrice">
#                     <div>Итог: </div>
#                     <div class="price"> <span> 2900</span></div>
#                 </div>
#                 <hr>
#             </div>
#         </div>
#     </body>
# </html>
#     """

    with open("template.html", "r", encoding="UTF-8") as file:
        with open("template-styles.css", "r") as styles_file:
            contents = file.read().format(idx, f"{l_name} {f_name}", phone, prs, total, "")

    # with open("tmp.html", "w") as file:
    #     file.write(contents)

    imgkit.from_string(contents, f"imgs/{idx}.png", css="template-styles.css", options={
        "width": int(1748 / 1.5),
        "height": int(2480 / 1.5)
    })
