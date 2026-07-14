using ECCD.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace ECCD.Infrastructure.Persistence.Configurations;

public class ClassroomConfiguration : IEntityTypeConfiguration<Classroom>
{
    public void Configure(EntityTypeBuilder<Classroom> builder)
    {
        builder.HasKey(c => c.Id);

        builder.Property(c => c.Name).HasMaxLength(200).IsRequired();
        builder.Property(c => c.Description).HasMaxLength(1000);
        builder.Property(c => c.AgeGroup).HasMaxLength(50);
        builder.Property(c => c.SchoolYear).HasMaxLength(20);
        builder.Property(c => c.Schedule).HasMaxLength(200);
        builder.Property(c => c.ThemeColor).HasMaxLength(7); // #RRGGBB
        builder.Property(c => c.BannerUrl).HasMaxLength(500);

        builder.HasOne(c => c.Teacher)
            .WithMany(t => t.Classrooms)
            .HasForeignKey(c => c.TeacherId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasOne(c => c.Cdc)
            .WithMany(cdc => cdc.Classrooms)
            .HasForeignKey(c => c.CdcId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasQueryFilter(c => !c.IsDeleted);
    }
}
