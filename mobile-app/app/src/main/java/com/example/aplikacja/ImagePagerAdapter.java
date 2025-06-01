package com.example.aplikacja;

// Adapter do wyświetlania listy obrazów w formie pagera (np. ViewPager2/RecyclerView)
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import java.util.List;

public class ImagePagerAdapter extends RecyclerView.Adapter<ImagePagerAdapter.ImageViewHolder> {

    // Kontekst aplikacji/aktywności
    private Context context;
    // Lista URL-i obrazów do wyświetlenia
    private List<String> imageUrls;

    // Konstruktor adaptera
    public ImagePagerAdapter(Context context, List<String> imageUrls) {
        this.context = context;
        this.imageUrls = imageUrls;
    }

    @NonNull
    @Override
    public ImageViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // Tworzy widok pojedynczej strony z obrazem
        View view = LayoutInflater.from(context).inflate(R.layout.item_image_page, parent, false);
        return new ImageViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ImageViewHolder holder, int position) {
        // Ładuje obraz do ImageView przy użyciu Glide
        Glide.with(context)
                .load(imageUrls.get(position))
                .centerCrop()
                .into(holder.imageView);
    }

    @Override
    public int getItemCount() {
        // Zwraca liczbę obrazów
        return imageUrls.size();
    }

    // ViewHolder przechowujący referencję do ImageView
    public static class ImageViewHolder extends RecyclerView.ViewHolder {
        ImageView imageView;
        public ImageViewHolder(@NonNull View itemView) {
            super(itemView);
            imageView = itemView.findViewById(R.id.imageViewPage);
        }
    }
}
