import os
import re

import numpy as np
import pandas as pd
import cv2 as cv

from img_generator import gen_img


class Product:
    def __init__(self, title: str, price=None):
        self.title = title

        self.price = price

        split_title = self.title.split()
        filtered = ""
        i = 0
        for word in split_title:
            if word.lower() == "цена":
                self.price = float(re.sub("[^0-9\.]", "", split_title[i + 1]))
                break

            if not re.match("\d{2}-\d{2}см", word.lower()):
                filtered += f"{word} "

            i += 1

        if price and str(price) != "nan":
            assert round(self.price, 0) == round(price, 0), f"{self.price} != {price}"
            self.price = price

        self.filtered_title = filtered.strip()

    def __str__(self):
        return f"""Product(
        title: {self.title},
        filtered_title: {self.filtered_title}
        price: {self.price}
        )"""


def capfirst(string: str) -> str:
    return string[0].capitalize() + string[1:]


def gen_individual_imgs(data_filename: str):
    data = pd.read_csv(data_filename)
    cols = list(map(str, data.columns))

    start_idx = 0
    end_idx = len(cols) - 1

    while "цена" not in cols[start_idx].lower():
        start_idx += 1

    # while "цена" not in cols[end_idx].lower():
    #     end_idx -= 1

    products = {}

    for product_title in cols[start_idx: end_idx + 1]:
        if "цена" not in product_title.lower():
            continue

        price_start_idx = product_title.lower().find("цена")
        price_str = product_title[price_start_idx:]
        price = re.sub("[^0-9\.\,]", "", price_str).replace(",", ".")
        products[product_title] = Product(product_title[:price_start_idx], price=float(price))

    for i in range(len(data["Фамилия"])):
        l_name = str(data["Фамилия"][i]).lower().strip()
        f_name = str(data["Имя"][i]).lower().strip()

        if f_name == "nan" and l_name == "nan":
            continue

        f_name = capfirst(f_name)
        l_name = capfirst(l_name)

        phone = re.sub("\D", "", str(data["Телефон"][i]).split(",")[0].lower().strip())[:-1]

        try:
            if phone[0] != "9":
                phone = phone[1:]
        except:
            continue

        phone = "8-" + phone[:3] + "-" + phone[3:6] + "-" + phone[6:8] + "-" + phone[8:]
        # their_total = float(re.sub("[^0-9\.]", "", str(data["Сумма к оплате"][i])))
        their_total = 0
        total = 0

        # print(l_name, f_name, phone, total)
        prs = []

        for product_title in products:
            amount_str = re.sub("[^0-9\.]", "", str(data[product_title][i]))
            amount = int(float(amount_str)) if amount_str != "" else None
            if amount is None:
                continue

            pr = products[product_title]
            prs.append({
                "title": pr.filtered_title,
                "amount": amount,
                "price": pr.price
            })

            total += amount * pr.price

        if round(total, 0) != round(their_total, 0):
            print()
            print(f"{i} - Not matching total: {round(total, 0)} vs. {round(their_total, 0)}!")

        # gen_img(i, f_name, l_name, phone, total, prs)
        try:
            gen_img(i + 2, f_name, l_name, phone, round(total, 2), prs)
        except Exception as exc:
            print(exc)


def combine_images():
    assert os.path.exists("imgs/"), "source folder does not exist"
    imgs_filenames = sorted(os.listdir("imgs"), key=lambda x: int(x[:x.find(".")]))
    imgs_count = len(imgs_filenames)
    imgs_left = imgs_count

    print(imgs_filenames)

    for batch_start in range(0, imgs_count, 4):
        current_count = min(imgs_left, 4)
        ref_w, ref_h = 0, 0

        current_filenames = imgs_filenames[batch_start: batch_start + current_count]
        print(current_filenames)

        imgs = list(map(lambda x: cv.cvtColor(cv.imread(f"imgs/{x}"), cv.COLOR_BGR2GRAY), current_filenames))

        ch, cw = imgs[0].shape
        ref_h = max(ref_h, ch)
        ref_w = max(ref_w, cw)

        for i in range(len(imgs) - 1, 4):
            imgs.append(np.zeros((ref_h, ref_h)))

        ref_h_halved = ref_h // 2
        ref_w_halved = ref_w // 2

        dim = (ref_w_halved, ref_h_halved)
        new_shape = (dim[0] * dim[1])

        imgs[0] = cv.resize(imgs[0], dim).reshape(new_shape)
        imgs[1] = cv.resize(imgs[1], dim).reshape(new_shape)
        imgs[2] = cv.resize(imgs[2], dim).reshape(new_shape)
        imgs[3] = cv.resize(imgs[3], dim).reshape(new_shape)

        out = np.zeros((ref_h * ref_w))

        for row_idx in range(ref_h_halved):
            for col_idx in range(ref_w_halved):
                local_idx = row_idx * ref_w_halved + col_idx

                out[row_idx * ref_w + col_idx] = imgs[0][local_idx]
                out[row_idx * ref_w + col_idx + ref_w_halved] = imgs[1][local_idx]
                out[(row_idx + ref_h_halved) * ref_w + col_idx] = imgs[2][local_idx]
                out[(row_idx + ref_h_halved) * ref_w + col_idx + ref_w_halved] = imgs[3][local_idx]

        for col_idx in range(ref_w):
            out[(ref_h_halved - 1) * ref_w + col_idx] = 0
            out[ref_h_halved * ref_w + col_idx] = 0
            out[(ref_h_halved + 1) * ref_w + col_idx] = 0

        for row_idx in range(ref_h):
            out[row_idx * ref_w + ref_w_halved - 1] = 0
            out[row_idx * ref_w + ref_w_halved] = 0
            out[row_idx * ref_w + ref_w_halved + 1] = 0

        out = out.reshape((ref_h, ref_w))
        cv.imwrite(f"out/{batch_start}.png", out)

        imgs_left -= 4


regen_individual_imgs = True


def main():
    if regen_individual_imgs:
        if not os.path.exists("imgs/"):
            os.mkdir("imgs")

        for filename in os.listdir("imgs"):
            os.remove(f"imgs/{filename}")

        gen_individual_imgs("data.csv")

    combine_images()


if __name__ == '__main__':
    main()
